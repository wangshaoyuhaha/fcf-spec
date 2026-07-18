from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType

import pytest

from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1 import (
    InstitutionalCalendarEvent,
    InstitutionalCalendarSource,
)
from apps.v2_r24_local_multi_clock_event_state_foundation_app_1 import (
    RegisteredClockEventState,
)
from apps.v2_r26_local_consensus_expectation_gap_foundation_app_1 import (
    ConsensusProvider,
    ExpectationGapRecord,
    RegisteredActualObservation,
    RegisteredConsensusSnapshot,
)
from apps.v2_r27_local_event_reaction_quality_foundation_app_1 import (
    V2_R27_LOCAL_EVENT_REACTION_QUALITY_BOUNDARY,
    EventReactionQualityRecord,
    LocalEventReactionQualityRegistry,
    RegisteredReactionObservation,
    RegisteredReactionWindow,
    V2R27LocalEventReactionQualityBoundary,
    build_operator_acceptance,
    build_read_model,
    resolve_event_reaction_quality,
)


def _event() -> InstitutionalCalendarEvent:
    source = InstitutionalCalendarSource(
        source_id="registered-official-source",
        source_kind="OFFICIAL",
        registered_artifact_id="registered-earnings-source",
        artifact_version="artifact-v1",
        license_id="official-local-research-license",
        permitted_use="local-paper-research",
        retention_days=3650,
    )
    return InstitutionalCalendarEvent(
        record_id="earnings-event-r0",
        calendar_id="institutional-calendar-v1",
        event_id="earnings-event",
        event_type="EARNINGS_DISCLOSURE",
        market="a-share",
        horizon="earnings-window",
        event_at_utc="2026-01-02T09:00:00Z",
        publication_at_utc="2026-01-02T08:00:00Z",
        first_legally_available_at_utc="2026-01-02T08:01:00Z",
        retrieved_at_utc="2026-01-02T08:02:00Z",
        ingested_at_utc="2026-01-02T08:03:00Z",
        first_tradable_at_utc="2026-01-02T09:30:00Z",
        source=source,
        content_sha256="a" * 64,
    )


def _clock() -> RegisteredClockEventState:
    return RegisteredClockEventState(
        state_id="company-reaction-state",
        state_version="state-v1",
        clock_type="COMPANY",
        state_kind="FIRST_TRADABLE_REACTION",
        evidence_group="NEUTRAL",
        hypothesis_id="earnings-reaction-hypothesis",
        market="a-share",
        horizon="earnings-window",
        effective_from_utc="2026-01-02T09:30:00Z",
        effective_to_utc="2026-01-03T16:00:00Z",
        available_at_utc="2026-01-02T08:04:00Z",
        source_event=_event(),
        confidence_bps=7000,
    )


def _gap(*, actual_value: str = "106") -> ExpectationGapRecord:
    event = _event()
    provider = ConsensusProvider(
        provider_id="registered-consensus-provider",
        source_kind="LICENSED",
        registered_artifact_id="registered-consensus-artifact",
        artifact_version="artifact-v1",
        license_id="licensed-local-research",
        permitted_use="local-paper-research",
    )
    consensus = RegisteredConsensusSnapshot(
        snapshot_id="consensus-r0",
        subject_id="issuer-000001",
        metric_id="adjusted-profit",
        market="a-share",
        horizon="earnings-window",
        unit="cny-million",
        period_end_utc="2025-12-31T00:00:00Z",
        consensus_as_of_utc="2026-01-02T07:00:00Z",
        published_at_utc="2026-01-02T08:05:00Z",
        first_legally_available_at_utc="2026-01-02T08:06:00Z",
        retrieved_at_utc="2026-01-02T08:07:00Z",
        ingested_at_utc="2026-01-02T08:10:00Z",
        provider=provider,
        source_event=event,
        estimate_count=12,
        coverage_bps=8000,
        mean_value="100",
        median_value="98",
        lower_value="90",
        upper_value="110",
        dispersion_value="4",
    )
    actual = RegisteredActualObservation(
        observation_id="actual-r0",
        subject_id="issuer-000001",
        metric_id="adjusted-profit",
        market="a-share",
        horizon="earnings-window",
        unit="cny-million",
        value=actual_value,
        observed_at_utc="2026-01-02T09:00:00Z",
        available_at_utc="2026-01-02T09:05:00Z",
        source_event=event,
    )
    return ExpectationGapRecord(
        gap_id="expectation-gap-r0",
        consensus=consensus,
        actual=actual,
        available_at_utc="2026-01-02T09:05:00Z",
    )


def _window(**changes: object) -> RegisteredReactionWindow:
    values: dict[str, object] = {
        "window_id": "reaction-window-r0",
        "subject_id": "issuer-000001",
        "market": "a-share",
        "horizon": "earnings-window",
        "source_event": _event(),
        "clock_state": _clock(),
        "expectation_gap": _gap(),
        "reference_at_utc": "2026-01-02T09:25:00Z",
        "first_tradable_at_utc": "2026-01-02T09:30:00Z",
        "window_end_utc": "2026-01-02T15:00:00Z",
        "matures_at_utc": "2026-01-03T15:00:00Z",
        "available_at_utc": "2026-01-02T09:06:00Z",
    }
    values.update(changes)
    return RegisteredReactionWindow(**values)  # type: ignore[arg-type]


def _observation(**changes: object) -> RegisteredReactionObservation:
    values: dict[str, object] = {
        "observation_id": "reaction-observation-r0",
        "window": _window(),
        "observed_at_utc": "2026-01-02T15:01:00Z",
        "available_at_utc": "2026-01-02T15:02:00Z",
        "previous_close": "100",
        "first_tradable_price": "105",
        "high_price": "107",
        "low_price": "97",
        "close_price": "99",
        "volume_ratio_bps": 16000,
        "turnover_bps": 350,
        "spread_bps": 24,
        "depth_imbalance_bps": -800,
        "breadth_bps": 4300,
        "futures_basis_bps": -35,
        "volatility_bps": 220,
        "cross_market_state": "DIVERGENT",
    }
    values.update(changes)
    return RegisteredReactionObservation(**values)  # type: ignore[arg-type]


def _registry(
    observation: RegisteredReactionObservation | None = None,
) -> LocalEventReactionQualityRegistry:
    observation = observation or _observation()
    quality = EventReactionQualityRecord(
        quality_id="reaction-quality-r0",
        observation=observation,
        available_at_utc="2026-01-03T15:01:00Z",
    )
    return (
        LocalEventReactionQualityRegistry()
        .append_window(observation.window)
        .append_observation(observation)
        .append_quality(quality)
    )


def test_d1_boundary_is_closed_and_immutable() -> None:
    boundary = V2_R27_LOCAL_EVENT_REACTION_QUALITY_BOUNDARY

    assert boundary.registered_artifact_only is True
    assert boundary.ai_generated_label_allowed is False
    assert boundary.participant_intent_inference_allowed is False
    assert boundary.immature_outcome_promotion_allowed is False
    assert boundary.factor_activation_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R27LocalEventReactionQualityBoundary(ai_generated_label_allowed=True)
    with pytest.raises(FrozenInstanceError):
        boundary.factor_activation_allowed = True  # type: ignore[misc]


def test_d2_window_requires_ordered_registered_lineage() -> None:
    with pytest.raises(ValueError, match="times must be ordered"):
        _window(window_end_utc="2026-01-02T09:29:00Z")
    with pytest.raises(ValueError, match="clock dimensions must match"):
        _window(horizon="other-window")


def test_d2_observed_reaction_requires_complete_valid_range() -> None:
    with pytest.raises(ValueError, match="complete registered measurements"):
        _observation(spread_bps=None)
    with pytest.raises(ValueError, match="inside observed range"):
        _observation(close_price="108")


def test_d2_non_observed_reaction_preserves_explicit_missing_fields() -> None:
    missing = _observation(
        reaction_state="MISSING",
        missing_fields=("prices", "liquidity"),
        previous_close=None,
        first_tradable_price=None,
        high_price=None,
        low_price=None,
        close_price=None,
        volume_ratio_bps=None,
        turnover_bps=None,
        spread_bps=None,
        depth_imbalance_bps=None,
        breadth_bps=None,
        futures_basis_bps=None,
        volatility_bps=None,
        cross_market_state="NOT_AVAILABLE",
    )

    assert missing.reaction_state == "MISSING"
    with pytest.raises(ValueError, match="cannot carry partial measurements"):
        replace(missing, close_price="99")


def test_d3_quality_metrics_and_favorable_weak_label_are_deterministic() -> None:
    quality = _registry().quality_records[0]

    assert quality.gap_return_bps == 500
    assert quality.close_return_bps == -100
    assert quality.intrawindow_range_bps == 1000
    assert quality.close_location_bps == 2000
    assert quality.persistence_state == "REVERSED"
    assert quality.reaction_label == "FAVORABLE_WEAK_REACTION"
    with pytest.raises(ValueError, match="cannot activate a factor"):
        replace(quality, factor_activated=True)


def test_d3_unfavorable_resilient_reaction_is_observable() -> None:
    window = _window(expectation_gap=_gap(actual_value="90"))
    observation = _observation(
        window=window,
        first_tradable_price="96",
        high_price="103",
        low_price="94",
        close_price="101",
    )
    quality = EventReactionQualityRecord(
        quality_id="reaction-quality-resilient",
        observation=observation,
        available_at_utc="2026-01-03T15:01:00Z",
    )

    assert quality.reaction_label == "UNFAVORABLE_RESILIENT_REACTION"


def test_d3_registry_requires_registered_parent_lineage() -> None:
    observation = _observation()
    with pytest.raises(ValueError, match="window must be registered"):
        LocalEventReactionQualityRegistry(observations=(observation,))
    with pytest.raises(ValueError, match="duplicate reaction window id"):
        LocalEventReactionQualityRegistry(windows=(observation.window, observation.window))


def test_d4_resolver_preserves_immature_outcome() -> None:
    registry = LocalEventReactionQualityRegistry().append_window(_window())
    snapshot = resolve_event_reaction_quality(
        registry,
        subject_id="issuer-000001",
        market="a-share",
        horizon="earnings-window",
        as_of_utc="2026-01-02T15:30:00Z",
    )

    assert snapshot.state == "IMMATURE"
    assert snapshot.quality is None


def test_d4_resolver_reports_missing_window_and_observation() -> None:
    missing_window = resolve_event_reaction_quality(
        LocalEventReactionQualityRegistry(),
        subject_id="issuer-000001",
        market="a-share",
        horizon="earnings-window",
        as_of_utc="2026-01-03T16:00:00Z",
    )
    missing_observation = resolve_event_reaction_quality(
        LocalEventReactionQualityRegistry().append_window(_window()),
        subject_id="issuer-000001",
        market="a-share",
        horizon="earnings-window",
        as_of_utc="2026-01-03T16:00:00Z",
    )

    assert missing_window.state == "MISSING_WINDOW"
    assert missing_observation.state == "MISSING_OBSERVATION"


def test_d5_stale_and_conflict_states_remain_blocked() -> None:
    def blocked(state: str) -> RegisteredReactionObservation:
        return _observation(
            reaction_state=state,
            missing_fields=("registered-source-quality",),
            previous_close=None,
            first_tradable_price=None,
            high_price=None,
            low_price=None,
            close_price=None,
            volume_ratio_bps=None,
            turnover_bps=None,
            spread_bps=None,
            depth_imbalance_bps=None,
            breadth_bps=None,
            futures_basis_bps=None,
            volatility_bps=None,
            cross_market_state="NOT_AVAILABLE",
        )

    for state, expected in (("STALE", "STALE"), ("CONFLICT", "CONFLICT")):
        observation = blocked(state)
        registry = (
            LocalEventReactionQualityRegistry()
            .append_window(observation.window)
            .append_observation(observation)
        )
        snapshot = resolve_event_reaction_quality(
            registry,
            subject_id="issuer-000001",
            market="a-share",
            horizon="earnings-window",
            as_of_utc="2026-01-03T16:00:00Z",
        )
        assert snapshot.state == expected


def test_d5_zero_range_preserves_unavailable_close_location() -> None:
    observation = _observation(
        first_tradable_price="100",
        high_price="100",
        low_price="100",
        close_price="100",
    )
    quality = EventReactionQualityRecord(
        quality_id="reaction-quality-zero-range",
        observation=observation,
        available_at_utc="2026-01-03T15:01:00Z",
    )

    assert quality.close_location_bps is None


def test_d5_future_quality_is_not_visible_at_as_of() -> None:
    registry = _registry()
    snapshot = resolve_event_reaction_quality(
        registry,
        subject_id="issuer-000001",
        market="a-share",
        horizon="earnings-window",
        as_of_utc="2026-01-03T15:00:30Z",
    )

    assert snapshot.state == "MISSING_QUALITY"


def test_d6_read_model_and_operator_acceptance_are_read_only() -> None:
    registry = _registry()
    snapshot = resolve_event_reaction_quality(
        registry,
        subject_id="issuer-000001",
        market="a-share",
        horizon="earnings-window",
        as_of_utc="2026-01-03T16:00:00Z",
    )
    model = build_read_model(registry)
    acceptance = build_operator_acceptance(snapshot)

    assert snapshot.state == "RESOLVED"
    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["ai_generated_label"] is False
    assert model.payload["participant_intent_inference"] is False
    assert model.payload["factor_activation"] is False
    assert model.payload["order_or_execution"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    assert acceptance.automatic_approval is False
    with pytest.raises(TypeError):
        model.payload["factor_activation"] = True  # type: ignore[index]
