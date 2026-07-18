from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType

import pytest

from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1 import (
    InstitutionalCalendarEvent,
    InstitutionalCalendarSource,
)
from apps.v2_r33_local_holiday_liquidity_state_foundation_app_1 import (
    HolidayLiquidityMeasurement,
    LocalHolidayLiquidityRegistry,
    RegisteredHolidayLiquidityObservation,
    V2_R33_LOCAL_HOLIDAY_LIQUIDITY_STATE_BOUNDARY,
    V2R33LocalHolidayLiquidityStateBoundary,
    build_operator_acceptance,
    build_read_model,
    resolve_holiday_liquidity,
)


def _event() -> InstitutionalCalendarEvent:
    source = InstitutionalCalendarSource(
        source_id="official-holiday-source",
        source_kind="OFFICIAL",
        registered_artifact_id="holiday-calendar-artifact",
        artifact_version="v1",
        license_id="local-license",
        permitted_use="local-paper-research",
        retention_days=3650,
    )
    return InstitutionalCalendarEvent(
        record_id="holiday-event-r0",
        calendar_id="a-share-calendar-v1",
        event_id="spring-festival-2026",
        event_type="HOLIDAY",
        market="a-share",
        horizon="daily",
        event_at_utc="2026-02-01T00:00:00Z",
        publication_at_utc="2026-01-01T00:00:00Z",
        first_legally_available_at_utc="2026-01-01T00:01:00Z",
        retrieved_at_utc="2026-01-01T00:02:00Z",
        ingested_at_utc="2026-01-01T00:03:00Z",
        first_tradable_at_utc="2026-01-02T01:30:00Z",
        source=source,
        content_sha256="a" * 64,
    )


def _observation(**changes: object):
    values: dict[str, object] = {
        "observation_id": "holiday-liquidity-r0",
        "subject_id": "csi-300",
        "market": "a-share",
        "horizon": "daily",
        "holiday_name": "spring-festival",
        "observed_at_utc": "2026-01-29T07:00:00Z",
        "available_at_utc": "2026-01-29T07:01:00Z",
        "holiday_length_days": 7,
        "overseas_open_days": 5,
        "settlement_mismatch_days": 2,
        "expected_event_count": 1,
        "spread_bps": "20",
        "baseline_spread_bps": "10",
        "depth_units": "50",
        "baseline_depth_units": "100",
        "volume_units": "80",
        "baseline_volume_units": "100",
        "turnover_units": "60",
        "baseline_turnover_units": "100",
        "basis_bps": "-15",
        "baseline_basis_bps": "-5",
        "source_event": _event(),
    }
    values.update(changes)
    return RegisteredHolidayLiquidityObservation(**values)  # type: ignore[arg-type]


def _registry() -> LocalHolidayLiquidityRegistry:
    observation = _observation()
    measurement = HolidayLiquidityMeasurement(
        measurement_id="holiday-measurement-r0",
        observation=observation,
        available_at_utc="2026-01-29T07:02:00Z",
    )
    return (
        LocalHolidayLiquidityRegistry()
        .append_observation(observation)
        .append_measurement(measurement)
    )


def test_d1_boundary_is_closed_and_immutable():
    boundary = V2_R33_LOCAL_HOLIDAY_LIQUIDITY_STATE_BOUNDARY
    assert not boundary.fixed_threshold_allowed
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R33LocalHolidayLiquidityStateBoundary(
            fixed_last_three_days_rule_allowed=True
        )
    with pytest.raises(FrozenInstanceError):
        boundary.stress_direction_allowed = True  # type: ignore[misc]


def test_d2_requires_registered_holiday_event():
    with pytest.raises(ValueError, match="R23 HOLIDAY"):
        _observation(source_event=object())


def test_d2_rejects_invalid_calendar_range():
    with pytest.raises(ValueError, match="registered range"):
        _observation(holiday_length_days=31)


def test_d2_non_observed_state_is_explicit():
    changes = {name: None for name in (
        "spread_bps", "baseline_spread_bps", "depth_units",
        "baseline_depth_units", "volume_units", "baseline_volume_units",
        "turnover_units", "baseline_turnover_units", "basis_bps",
        "baseline_basis_bps",
    )}
    item = _observation(
        observation_state="MISSING",
        missing_fields=("registered-liquidity-values",),
        **changes,
    )
    assert item.observation_state == "MISSING"


def test_d3_measurements_are_deterministic():
    item = _registry().measurements[0]
    assert (
        item.spread_ratio_bps,
        item.depth_ratio_bps,
        item.volume_ratio_bps,
        item.turnover_ratio_bps,
        item.basis_change_bps,
    ) == (20000, 5000, 8000, 6000, -10)


def test_d3_zero_baseline_is_rejected():
    with pytest.raises(ValueError, match="positive"):
        _observation(baseline_volume_units="0")


def test_d3_fixed_rules_direction_and_factor_are_rejected():
    measurement = _registry().measurements[0]
    with pytest.raises(ValueError, match="last-three-days"):
        replace(measurement, fixed_last_three_days_rule=True)
    with pytest.raises(ValueError, match="fixed threshold"):
        replace(measurement, fixed_threshold=True)
    with pytest.raises(ValueError, match="stress direction"):
        replace(measurement, stress_direction=True)
    with pytest.raises(ValueError, match="activate"):
        replace(measurement, factor_activated=True)


def test_d3_registry_requires_registered_parent():
    measurement = _registry().measurements[0]
    with pytest.raises(ValueError, match="must be registered"):
        LocalHolidayLiquidityRegistry(measurements=(measurement,))


def test_d4_missing_resolver_state():
    snapshot = resolve_holiday_liquidity(
        LocalHolidayLiquidityRegistry(),
        subject_id="csi-300",
        market="a-share",
        as_of_utc="2026-01-30T00:00:00Z",
    )
    assert snapshot.state == "MISSING_OBSERVATION"


def test_d5_future_measurement_is_hidden():
    snapshot = resolve_holiday_liquidity(
        _registry(),
        subject_id="csi-300",
        market="a-share",
        as_of_utc="2026-01-29T07:01:30Z",
    )
    assert snapshot.state == "MISSING_MEASUREMENT"


def test_d5_conflict_state_is_preserved():
    changes = {name: None for name in (
        "spread_bps", "baseline_spread_bps", "depth_units",
        "baseline_depth_units", "volume_units", "baseline_volume_units",
        "turnover_units", "baseline_turnover_units", "basis_bps",
        "baseline_basis_bps",
    )}
    item = _observation(
        observation_state="CONFLICT",
        missing_fields=("conflicting-liquidity-values",),
        **changes,
    )
    snapshot = resolve_holiday_liquidity(
        LocalHolidayLiquidityRegistry().append_observation(item),
        subject_id="csi-300",
        market="a-share",
        as_of_utc="2026-01-30T00:00:00Z",
    )
    assert snapshot.state == "CONFLICT"


def test_d5_resolved_state_preserves_no_fixed_rule():
    snapshot = resolve_holiday_liquidity(
        _registry(),
        subject_id="csi-300",
        market="a-share",
        as_of_utc="2026-01-30T00:00:00Z",
    )
    assert "NO_FIXED_THRESHOLD" in snapshot.reason_codes


def test_d6_presentation_and_acceptance_are_read_only():
    registry = _registry()
    snapshot = resolve_holiday_liquidity(
        registry,
        subject_id="csi-300",
        market="a-share",
        as_of_utc="2026-01-30T00:00:00Z",
    )
    model = build_read_model(registry)
    acceptance = build_operator_acceptance(snapshot)
    assert snapshot.state == "RESOLVED"
    assert isinstance(model.payload, MappingProxyType)
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    with pytest.raises(TypeError):
        model.payload["fixed_threshold"] = True  # type: ignore[index]
