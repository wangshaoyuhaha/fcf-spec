from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType

import pytest

from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1 import (
    InstitutionalCalendarEvent,
    InstitutionalCalendarSource,
)
from apps.v2_r24_local_multi_clock_event_state_foundation_app_1 import (
    V2_R24_LOCAL_MULTI_CLOCK_EVENT_STATE_BOUNDARY,
    LocalMultiClockEventStateRegistry,
    RegisteredClockEventState,
    V2R24LocalMultiClockEventStateBoundary,
    build_operator_acceptance,
    build_read_model,
    resolve_multi_clock_event_state,
)


def _source() -> InstitutionalCalendarSource:
    return InstitutionalCalendarSource(
        source_id="registered-official-source",
        source_kind="OFFICIAL",
        registered_artifact_id="registered-clock-source",
        artifact_version="artifact-v1",
        license_id="official-local-research-license",
        permitted_use="local-paper-research",
        retention_days=3650,
    )


def _event(
    event_id: str = "institutional-event",
    record_id: str = "institutional-event-r0",
    event_type: str = "POLICY_MEETING",
) -> InstitutionalCalendarEvent:
    return InstitutionalCalendarEvent(
        record_id=record_id,
        calendar_id="institutional-calendar-v1",
        event_id=event_id,
        event_type=event_type,
        market="a-share",
        horizon="event-window",
        event_at_utc="2026-01-02T10:00:00Z",
        publication_at_utc="2026-01-02T08:00:00Z",
        first_legally_available_at_utc="2026-01-02T08:01:00Z",
        retrieved_at_utc="2026-01-02T08:02:00Z",
        ingested_at_utc="2026-01-02T08:03:00Z",
        first_tradable_at_utc="2026-01-02T08:05:00Z",
        source=_source(),
        content_sha256="a" * 64,
    )


def _state(**changes: object) -> RegisteredClockEventState:
    values: dict[str, object] = {
        "state_id": "institutional-pre-event",
        "state_version": "state-v1",
        "clock_type": "INSTITUTIONAL",
        "state_kind": "PRE_EVENT",
        "evidence_group": "NEUTRAL",
        "hypothesis_id": "registered-event-context",
        "market": "a-share",
        "horizon": "event-window",
        "effective_from_utc": "2026-01-02T08:00:00Z",
        "effective_to_utc": "2026-01-02T10:00:00Z",
        "available_at_utc": "2026-01-02T08:10:00Z",
        "source_event": _event(),
        "confidence_bps": 5000,
    }
    values.update(changes)
    return RegisteredClockEventState(**values)  # type: ignore[arg-type]


def test_d1_boundary_is_closed_and_immutable() -> None:
    boundary = V2_R24_LOCAL_MULTI_CLOCK_EVENT_STATE_BOUNDARY

    assert boundary.registered_artifact_only is True
    assert boundary.live_clock_allowed is False
    assert boundary.conflict_deletion_allowed is False
    assert boundary.winner_selection_allowed is False
    assert boundary.factor_or_score_allowed is False
    assert boundary.order_or_execution_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R24LocalMultiClockEventStateBoundary(winner_selection_allowed=True)
    with pytest.raises(FrozenInstanceError):
        boundary.live_clock_allowed = True  # type: ignore[misc]


def test_d2_contract_requires_registered_clock_and_state_kind() -> None:
    with pytest.raises(ValueError, match="clock_type is not registered"):
        _state(clock_type="GLOBAL")
    with pytest.raises(ValueError, match="state_kind is not registered"):
        _state(state_kind="UNREGISTERED")
    with pytest.raises(ValueError, match="cannot precede source ingest"):
        _state(available_at_utc="2026-01-02T08:02:30Z")


def test_d2_missing_stale_and_cancelled_semantics_fail_closed() -> None:
    with pytest.raises(ValueError, match="explicit missing state"):
        _state(evidence_group="MISSING", confidence_bps=0)
    with pytest.raises(ValueError, match="must remain stale or blocked"):
        _state(freshness_state="STALE", evidence_group="NEUTRAL")
    original = _event()
    cancelled = replace(
        original,
        record_id="institutional-event-r1",
        revision_number=1,
        revision_state="CANCELLED",
        revises_record_hash=original.record_hash,
    )
    with pytest.raises(ValueError, match="must remain blocked"):
        _state(source_event=cancelled)
    blocked = _state(source_event=cancelled, evidence_group="BLOCKED")
    assert blocked.evidence_group == "BLOCKED"


def test_d3_registry_rejects_duplicates_and_same_event_overlap() -> None:
    first = _state()
    registry = LocalMultiClockEventStateRegistry().append(first)

    with pytest.raises(ValueError, match="duplicate clock state id"):
        registry.append(first)
    with pytest.raises(ValueError, match="same event clock states cannot overlap"):
        registry.append(
            _state(
                state_id="institutional-overlap",
                state_kind="RELEASED_NOT_TRADABLE",
                effective_from_utc="2026-01-02T09:00:00Z",
                effective_to_utc="2026-01-02T11:00:00Z",
            )
        )


def test_d3_registry_allows_distinct_event_overlap() -> None:
    first = _state()
    second = _state(
        state_id="institutional-holiday",
        state_kind="HOLIDAY_LIQUIDITY",
        source_event=_event("holiday-event", "holiday-event-r0", "HOLIDAY"),
    )
    registry = LocalMultiClockEventStateRegistry().append(first).append(second)

    assert len(registry.states) == 2


def test_d4_resolution_is_point_in_time_and_half_open() -> None:
    registry = LocalMultiClockEventStateRegistry().append(_state())
    unavailable = resolve_multi_clock_event_state(
        registry,
        market="a-share",
        horizon="event-window",
        observed_at_utc="2026-01-02T08:04:00Z",
        as_of_utc="2026-01-02T08:05:00Z",
    )
    resolved = resolve_multi_clock_event_state(
        registry,
        market="a-share",
        horizon="event-window",
        observed_at_utc="2026-01-02T08:30:00Z",
        as_of_utc="2026-01-02T08:30:00Z",
    )
    expired = resolve_multi_clock_event_state(
        registry,
        market="a-share",
        horizon="event-window",
        observed_at_utc="2026-01-02T10:00:00Z",
        as_of_utc="2026-01-02T10:00:00Z",
    )

    assert unavailable.state == "MISSING"
    assert resolved.state == "RESOLVED"
    assert resolved.active_states[0].state_id == "institutional-pre-event"
    assert expired.state == "MISSING"


def test_d4_future_observation_is_rejected() -> None:
    with pytest.raises(ValueError, match="future observation"):
        resolve_multi_clock_event_state(
            LocalMultiClockEventStateRegistry().append(_state()),
            market="a-share",
            horizon="event-window",
            observed_at_utc="2026-01-02T09:00:00Z",
            as_of_utc="2026-01-02T08:59:59Z",
        )


def test_d5_overlap_and_missing_clocks_are_preserved_without_winner() -> None:
    institutional = _state()
    holiday = _state(
        state_id="institutional-holiday",
        state_kind="HOLIDAY_LIQUIDITY",
        evidence_group="OPPOSING",
        source_event=_event("holiday-event", "holiday-event-r0", "HOLIDAY"),
    )
    macro = _state(
        state_id="macro-release",
        clock_type="MACRO",
        evidence_group="SUPPORTING",
        source_event=_event("macro-event", "macro-event-r0", "MACRO_RELEASE"),
    )
    registry = (
        LocalMultiClockEventStateRegistry()
        .append(institutional)
        .append(holiday)
        .append(macro)
    )
    snapshot = resolve_multi_clock_event_state(
        registry,
        market="a-share",
        horizon="event-window",
        observed_at_utc="2026-01-02T08:30:00Z",
        as_of_utc="2026-01-02T08:30:00Z",
    )

    assert snapshot.clock_groups["INSTITUTIONAL"] == (
        "institutional-holiday",
        "institutional-pre-event",
    )
    assert snapshot.evidence_groups["SUPPORTING"] == ("macro-release",)
    assert snapshot.evidence_groups["OPPOSING"] == ("institutional-holiday",)
    assert snapshot.overlap_codes == ("OVERLAP_PRESERVED_INSTITUTIONAL",)
    assert snapshot.missing_clocks == ("CAPITAL", "INDUSTRY", "COMPANY")
    assert snapshot.winner_state_id is None
    assert snapshot.conflict_policy == "PRESERVE_ALL_NO_WINNER"


def test_d5_market_and_horizon_are_isolated_and_hash_is_deterministic() -> None:
    registry = LocalMultiClockEventStateRegistry().append(_state())
    first = resolve_multi_clock_event_state(
        registry,
        market="a-share",
        horizon="event-window",
        observed_at_utc="2026-01-02T08:30:00Z",
        as_of_utc="2026-01-02T08:30:00Z",
    )
    repeated = resolve_multi_clock_event_state(
        registry,
        market="a-share",
        horizon="event-window",
        observed_at_utc="2026-01-02T08:30:00Z",
        as_of_utc="2026-01-02T08:30:00Z",
    )
    isolated = resolve_multi_clock_event_state(
        registry,
        market="btc",
        horizon="event-window",
        observed_at_utc="2026-01-02T08:30:00Z",
        as_of_utc="2026-01-02T08:30:00Z",
    )

    assert first.snapshot_hash == repeated.snapshot_hash
    assert isolated.state == "MISSING"
    assert isolated.active_states == ()


def test_d6_read_model_and_acceptance_are_read_only() -> None:
    registry = LocalMultiClockEventStateRegistry().append(_state())
    snapshot = resolve_multi_clock_event_state(
        registry,
        market="a-share",
        horizon="event-window",
        observed_at_utc="2026-01-02T08:30:00Z",
        as_of_utc="2026-01-02T08:30:00Z",
    )
    model = build_read_model(registry)
    acceptance = build_operator_acceptance(snapshot)

    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["winner_selection"] is False
    assert model.payload["conflict_deletion"] is False
    assert model.payload["factor_or_score"] is False
    assert model.payload["order_or_execution"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    assert acceptance.automatic_approval is False
    assert acceptance.action_created is False
    with pytest.raises(TypeError):
        model.payload["winner_selection"] = True  # type: ignore[index]
