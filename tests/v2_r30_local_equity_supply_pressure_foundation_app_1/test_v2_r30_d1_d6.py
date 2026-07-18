from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType

import pytest

from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1 import InstitutionalCalendarEvent, InstitutionalCalendarSource
from apps.v2_r24_local_multi_clock_event_state_foundation_app_1 import RegisteredClockEventState
from apps.v2_r30_local_equity_supply_pressure_foundation_app_1 import (
    V2_R30_LOCAL_EQUITY_SUPPLY_PRESSURE_BOUNDARY,
    EquitySupplyPressureRecord,
    LocalEquitySupplyPressureRegistry,
    RegisteredEquitySupplyEvent,
    RegisteredEquitySupplyObservation,
    V2R30LocalEquitySupplyPressureBoundary,
    build_operator_acceptance,
    build_read_model,
    resolve_equity_supply_pressure,
)


def _source_event(event_at_utc: str = "2026-06-30T00:00:00Z") -> InstitutionalCalendarEvent:
    source = InstitutionalCalendarSource(source_id="official-unlock-source", source_kind="OFFICIAL", registered_artifact_id="unlock-artifact", artifact_version="artifact-v1", license_id="official-local-license", permitted_use="local-paper-research", retention_days=3650)
    return InstitutionalCalendarEvent(record_id="unlock-event-r0", calendar_id="exchange-calendar-v1", event_id="unlock-event", event_type="CORPORATE_ACTION", market="a-share", horizon="supply-window", event_at_utc=event_at_utc, publication_at_utc="2026-01-05T00:00:00Z", first_legally_available_at_utc="2026-01-05T00:01:00Z", retrieved_at_utc="2026-01-05T00:02:00Z", ingested_at_utc="2026-01-05T00:03:00Z", first_tradable_at_utc="2026-01-05T01:30:00Z", source=source, content_sha256="d" * 64)


def _event(**changes: object) -> RegisteredEquitySupplyEvent:
    source = _source_event()
    state = RegisteredClockEventState(state_id="unlock-state-r0", state_version="state-v1", clock_type="COMPANY", state_kind="PRE_EVENT", evidence_group="NEUTRAL", hypothesis_id="registered-supply-context", market="a-share", horizon="supply-window", effective_from_utc="2026-06-01T00:00:00Z", effective_to_utc="2026-06-30T00:00:00Z", available_at_utc="2026-01-05T00:04:00Z", source_event=source, confidence_bps=10000)
    values: dict[str, object] = {"supply_event_id": "unlock-r0", "subject_id": "issuer-000001", "market": "a-share", "supply_type": "LOCK_UP_EXPIRY", "holder_class": "ipo-original-holder", "legally_sellable_at_utc": "2026-06-30T00:00:00Z", "available_at_utc": "2026-01-05T00:05:00Z", "source_event": source, "event_state": state}
    values.update(changes)
    return RegisteredEquitySupplyEvent(**values)  # type: ignore[arg-type]


def _observation(**changes: object) -> RegisteredEquitySupplyObservation:
    values: dict[str, object] = {"observation_id": "supply-observation-r0", "supply_event": _event(), "observed_at_utc": "2026-07-01T07:00:00Z", "available_at_utc": "2026-07-01T07:01:00Z", "legally_sellable_shares": "100", "free_float_shares": "1000", "market_price": "10", "average_traded_value": "200", "pledged_shares": "200", "actual_sold_shares": "25"}
    values.update(changes)
    return RegisteredEquitySupplyObservation(**values)  # type: ignore[arg-type]


def _registry(observation: RegisteredEquitySupplyObservation | None = None) -> LocalEquitySupplyPressureRegistry:
    observation = observation or _observation()
    record = EquitySupplyPressureRecord(record_id="pressure-r0", observation=observation, available_at_utc="2026-07-01T07:02:00Z")
    return LocalEquitySupplyPressureRegistry().append_event(observation.supply_event).append_observation(observation).append_record(record)


def test_d1_boundary_is_closed_and_immutable() -> None:
    boundary = V2_R30_LOCAL_EQUITY_SUPPLY_PRESSURE_BOUNDARY
    assert boundary.unlock_equals_sale_claim_allowed is False
    assert boundary.forced_sale_claim_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R30LocalEquitySupplyPressureBoundary(forced_sale_claim_allowed=True)
    with pytest.raises(FrozenInstanceError):
        boundary.forced_sale_claim_allowed = True  # type: ignore[misc]


def test_d2_supply_type_must_be_registered() -> None:
    with pytest.raises(ValueError, match="supply_type is not registered"):
        _event(supply_type="UNKNOWN")


def test_d2_legally_sellable_time_requires_registered_event_time() -> None:
    with pytest.raises(ValueError, match="must equal registered event time"):
        _event(legally_sellable_at_utc="2026-07-01T00:00:00Z")


def test_d2_event_state_must_share_source_lineage() -> None:
    event = _event()
    other_source = _source_event("2026-07-31T00:00:00Z")
    wrong_state = replace(event.event_state, source_event=other_source)
    with pytest.raises(ValueError, match="share the registered supply event"):
        replace(event, event_state=wrong_state)


def test_d2_observed_supply_requires_complete_valid_measurements() -> None:
    with pytest.raises(ValueError, match="complete measurements"):
        _observation(market_price=None)
    with pytest.raises(ValueError, match="cannot exceed"):
        _observation(actual_sold_shares="101")


def test_d2_missing_supply_is_explicit_and_has_no_partial_values() -> None:
    names = ("legally_sellable_shares", "free_float_shares", "market_price", "average_traded_value", "pledged_shares", "actual_sold_shares")
    missing = _observation(observation_state="MISSING", missing_fields=("registered-supply-source",), **{name: None for name in names})
    assert missing.observation_state == "MISSING"
    with pytest.raises(ValueError, match="cannot carry partial measurements"):
        replace(missing, market_price="10")


def test_d3_pressure_metrics_are_deterministic() -> None:
    record = _registry().records[0]
    assert record.supply_to_float_bps == 1000
    assert str(record.supply_market_value) == "1000"
    assert str(record.absorption_days) == "5.0000"
    assert record.pledge_to_float_bps == 2000
    assert record.actual_sale_to_supply_bps == 2500


def test_d3_record_cannot_claim_sale_force_intent_or_activate_factor() -> None:
    record = _registry().records[0]
    with pytest.raises(ValueError, match="actual sale"):
        replace(record, unlock_equals_sale_claim=True)
    with pytest.raises(ValueError, match="forced-sale claim"):
        replace(record, forced_sale_claim=True)
    with pytest.raises(ValueError, match="holder-intent claim"):
        replace(record, holder_intent_claim=True)
    with pytest.raises(ValueError, match="activate a factor"):
        replace(record, factor_activated=True)


def test_d3_registry_requires_registered_parent_lineage() -> None:
    observation = _observation()
    with pytest.raises(ValueError, match="event must be registered"):
        LocalEquitySupplyPressureRegistry(observations=(observation,))


def test_d4_resolver_preserves_missing_observation() -> None:
    snapshot = resolve_equity_supply_pressure(LocalEquitySupplyPressureRegistry(), subject_id="issuer-000001", market="a-share", as_of_utc="2026-07-02T00:00:00Z")
    assert snapshot.state == "MISSING_OBSERVATION"


def test_d5_future_metrics_are_not_visible_at_as_of() -> None:
    snapshot = resolve_equity_supply_pressure(_registry(), subject_id="issuer-000001", market="a-share", as_of_utc="2026-07-01T07:01:30Z")
    assert snapshot.state == "MISSING_METRICS"


def test_d5_stale_supply_remains_blocked() -> None:
    names = ("legally_sellable_shares", "free_float_shares", "market_price", "average_traded_value", "pledged_shares", "actual_sold_shares")
    observation = _observation(observation_state="STALE", missing_fields=("fresh-supply-source",), **{name: None for name in names})
    registry = LocalEquitySupplyPressureRegistry().append_event(observation.supply_event).append_observation(observation)
    snapshot = resolve_equity_supply_pressure(registry, subject_id="issuer-000001", market="a-share", as_of_utc="2026-07-02T00:00:00Z")
    assert snapshot.state == "STALE"


def test_d6_read_model_and_operator_acceptance_are_read_only() -> None:
    registry = _registry()
    snapshot = resolve_equity_supply_pressure(registry, subject_id="issuer-000001", market="a-share", as_of_utc="2026-07-02T00:00:00Z")
    model, acceptance = build_read_model(registry), build_operator_acceptance(snapshot)
    assert snapshot.state == "RESOLVED"
    assert "UNLOCK_DOES_NOT_IMPLY_SALE" in snapshot.reason_codes
    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["factor_activation"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    with pytest.raises(TypeError):
        model.payload["unlock_equals_sale_claim"] = True  # type: ignore[index]
