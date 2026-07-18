from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType

import pytest

from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1 import (
    InstitutionalCalendarEvent,
    InstitutionalCalendarSource,
)
from apps.v2_r24_local_multi_clock_event_state_foundation_app_1 import RegisteredClockEventState
from apps.v2_r29_local_index_futures_basis_roll_expiry_foundation_app_1 import (
    V2_R29_LOCAL_INDEX_FUTURES_BASIS_ROLL_EXPIRY_BOUNDARY,
    IndexFuturesBasisRollRecord,
    LocalIndexFuturesBasisRollExpiryRegistry,
    RegisteredFuturesCurveObservation,
    RegisteredIndexFuturesContract,
    V2R29LocalIndexFuturesBasisRollExpiryBoundary,
    build_operator_acceptance,
    build_read_model,
    resolve_index_futures_basis_roll_expiry,
)


def _event(contract_id: str, expiry_at_utc: str) -> InstitutionalCalendarEvent:
    source = InstitutionalCalendarSource(
        source_id=f"official-{contract_id}-source",
        source_kind="OFFICIAL",
        registered_artifact_id=f"{contract_id}-calendar-artifact",
        artifact_version="artifact-v1",
        license_id="official-local-license",
        permitted_use="local-paper-research",
        retention_days=3650,
    )
    return InstitutionalCalendarEvent(
        record_id=f"{contract_id}-expiry-r0",
        calendar_id="cffex-calendar-v1",
        event_id=f"{contract_id}-expiry",
        event_type="INDEX_FUTURES_EVENT",
        market="a-share-index-futures",
        horizon="expiry-window",
        event_at_utc=expiry_at_utc,
        publication_at_utc="2026-01-05T00:00:00Z",
        first_legally_available_at_utc="2026-01-05T00:01:00Z",
        retrieved_at_utc="2026-01-05T00:02:00Z",
        ingested_at_utc="2026-01-05T00:03:00Z",
        first_tradable_at_utc="2026-01-05T01:30:00Z",
        source=source,
        content_sha256="c" * 64,
    )


def _contract(contract_id: str, expiry_at_utc: str, **changes: object) -> RegisteredIndexFuturesContract:
    event = _event(contract_id, expiry_at_utc)
    state = RegisteredClockEventState(
        state_id=f"{contract_id}-expiry-state",
        state_version="state-v1",
        clock_type="INSTITUTIONAL",
        state_kind="EXPIRY_WINDOW",
        evidence_group="NEUTRAL",
        hypothesis_id="registered-expiry-context",
        market="a-share-index-futures",
        horizon="expiry-window",
        effective_from_utc="2026-06-01T00:00:00Z",
        effective_to_utc=expiry_at_utc,
        available_at_utc="2026-01-05T00:04:00Z",
        source_event=event,
        confidence_bps=10000,
    )
    values: dict[str, object] = {
        "contract_id": contract_id,
        "contract_family": "if",
        "market": "a-share-index-futures",
        "underlying_index_id": "csi-300",
        "expiry_at_utc": expiry_at_utc,
        "available_at_utc": "2026-01-05T00:05:00Z",
        "settlement_rule_version": "cffex-rule-v1",
        "contract_multiplier": "300",
        "expiry_event": event,
        "expiry_state": state,
    }
    values.update(changes)
    return RegisteredIndexFuturesContract(**values)  # type: ignore[arg-type]


def _observation(**changes: object) -> RegisteredFuturesCurveObservation:
    values: dict[str, object] = {
        "observation_id": "if-curve-r0",
        "front_contract": _contract("if-2606", "2026-06-19T07:00:00Z"),
        "next_contract": _contract("if-2607", "2026-07-17T07:00:00Z"),
        "observed_at_utc": "2026-06-14T07:00:00Z",
        "available_at_utc": "2026-06-14T07:01:00Z",
        "spot_index_price": "4000",
        "front_futures_price": "4020",
        "next_futures_price": "4040",
        "front_open_interest": "600",
        "next_open_interest": "400",
        "front_volume": "700",
        "next_volume": "300",
    }
    values.update(changes)
    return RegisteredFuturesCurveObservation(**values)  # type: ignore[arg-type]


def _registry(observation: RegisteredFuturesCurveObservation | None = None) -> LocalIndexFuturesBasisRollExpiryRegistry:
    observation = observation or _observation()
    record = IndexFuturesBasisRollRecord(
        record_id="if-basis-roll-r0",
        observation=observation,
        available_at_utc="2026-06-14T07:02:00Z",
    )
    return (
        LocalIndexFuturesBasisRollExpiryRegistry()
        .append_contract(observation.front_contract)
        .append_contract(observation.next_contract)
        .append_observation(observation)
        .append_record(record)
    )


def test_d1_boundary_is_closed_and_immutable() -> None:
    boundary = V2_R29_LOCAL_INDEX_FUTURES_BASIS_ROLL_EXPIRY_BOUNDARY
    assert boundary.fixed_third_friday_override_allowed is False
    assert boundary.bottom_claim_allowed is False
    assert boundary.participant_intent_claim_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R29LocalIndexFuturesBasisRollExpiryBoundary(bottom_claim_allowed=True)
    with pytest.raises(FrozenInstanceError):
        boundary.bottom_claim_allowed = True  # type: ignore[misc]


def test_d2_contract_expiry_must_equal_registered_calendar_event() -> None:
    with pytest.raises(ValueError, match="must equal registered expiry event"):
        _contract(
            "if-2606",
            "2026-06-19T07:00:00Z",
            expiry_event=_event("if-2606-revised", "2026-06-20T07:00:00Z"),
        )


def test_d2_contract_requires_expiry_window_state() -> None:
    contract = _contract("if-2606", "2026-06-19T07:00:00Z")
    wrong_state = replace(contract.expiry_state, state_kind="PRE_EVENT")
    with pytest.raises(ValueError, match="EXPIRY_WINDOW"):
        replace(contract, expiry_state=wrong_state)


def test_d2_curve_requires_ordered_matching_contracts() -> None:
    with pytest.raises(ValueError, match="next contract expiry must follow"):
        _observation(next_contract=_contract("if-2606b", "2026-06-19T07:00:00Z"))
    with pytest.raises(ValueError, match="share market, family, and underlying"):
        _observation(next_contract=_contract("ic-2607", "2026-07-17T07:00:00Z", contract_family="ic"))


def test_d2_observed_curve_requires_complete_comparable_measurements() -> None:
    with pytest.raises(ValueError, match="complete measurements"):
        _observation(spot_index_price=None)
    with pytest.raises(ValueError, match="prices must be positive"):
        _observation(front_futures_price="0")


def test_d2_missing_curve_is_explicit_and_has_no_partial_values() -> None:
    names = (
        "spot_index_price",
        "front_futures_price",
        "next_futures_price",
        "front_open_interest",
        "next_open_interest",
        "front_volume",
        "next_volume",
    )
    missing = _observation(
        observation_state="MISSING",
        missing_fields=("registered-curve-evidence",),
        **{name: None for name in names},
    )
    assert missing.observation_state == "MISSING"
    with pytest.raises(ValueError, match="cannot carry partial measurements"):
        replace(missing, spot_index_price="4000")


def test_d3_basis_roll_metrics_are_deterministic() -> None:
    record = _registry().records[0]
    assert str(record.basis_amount) == "20"
    assert record.basis_bps == 50
    assert record.annualized_basis_bps == 3650
    assert str(record.calendar_spread_amount) == "20"
    assert record.next_open_interest_share_bps == 4000
    assert record.next_volume_share_bps == 3000
    assert record.seconds_to_expiry == 432000


def test_d3_basis_roll_record_cannot_claim_bottom_intent_or_activate_factor() -> None:
    record = _registry().records[0]
    with pytest.raises(ValueError, match="bottom claim"):
        replace(record, bottom_claim=True)
    with pytest.raises(ValueError, match="participant-intent claim"):
        replace(record, participant_intent_claim=True)
    with pytest.raises(ValueError, match="activate a factor"):
        replace(record, factor_activated=True)


def test_d3_registry_requires_registered_contract_lineage() -> None:
    observation = _observation()
    with pytest.raises(ValueError, match="contracts must be registered"):
        LocalIndexFuturesBasisRollExpiryRegistry(observations=(observation,))


def test_d4_resolver_preserves_missing_observation() -> None:
    snapshot = resolve_index_futures_basis_roll_expiry(
        LocalIndexFuturesBasisRollExpiryRegistry(),
        contract_family="if",
        market="a-share-index-futures",
        as_of_utc="2026-06-15T00:00:00Z",
    )
    assert snapshot.state == "MISSING_OBSERVATION"


def test_d5_future_metrics_are_not_visible_at_as_of() -> None:
    snapshot = resolve_index_futures_basis_roll_expiry(
        _registry(),
        contract_family="if",
        market="a-share-index-futures",
        as_of_utc="2026-06-14T07:01:30Z",
    )
    assert snapshot.state == "MISSING_METRICS"


def test_d5_stale_curve_remains_blocked() -> None:
    names = (
        "spot_index_price",
        "front_futures_price",
        "next_futures_price",
        "front_open_interest",
        "next_open_interest",
        "front_volume",
        "next_volume",
    )
    observation = _observation(
        observation_state="STALE",
        missing_fields=("fresh-curve-source",),
        **{name: None for name in names},
    )
    registry = (
        LocalIndexFuturesBasisRollExpiryRegistry()
        .append_contract(observation.front_contract)
        .append_contract(observation.next_contract)
        .append_observation(observation)
    )
    snapshot = resolve_index_futures_basis_roll_expiry(
        registry,
        contract_family="if",
        market="a-share-index-futures",
        as_of_utc="2026-06-15T00:00:00Z",
    )
    assert snapshot.state == "STALE"


def test_d6_read_model_and_operator_acceptance_are_read_only() -> None:
    registry = _registry()
    snapshot = resolve_index_futures_basis_roll_expiry(
        registry,
        contract_family="if",
        market="a-share-index-futures",
        as_of_utc="2026-06-15T00:00:00Z",
    )
    model = build_read_model(registry)
    acceptance = build_operator_acceptance(snapshot)
    assert snapshot.state == "RESOLVED"
    assert "NO_BOTTOM_CLAIM" in snapshot.reason_codes
    assert "NO_PARTICIPANT_INTENT_CLAIM" in snapshot.reason_codes
    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["factor_activation"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    with pytest.raises(TypeError):
        model.payload["bottom_claim"] = True  # type: ignore[index]
