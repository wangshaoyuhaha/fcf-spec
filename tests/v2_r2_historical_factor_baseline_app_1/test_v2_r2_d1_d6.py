from dataclasses import FrozenInstanceError, replace
from decimal import Decimal
from types import MappingProxyType

import pytest

from apps.v2_r2_historical_factor_baseline_app_1 import (
    BaselineRequest,
    DataRightsDeclaration,
    HistoricalObservation,
    HistoricalObservationRegistry,
    V2R2HistoricalBaselineBoundary,
    V2_R2_HISTORICAL_BASELINE_BOUNDARY,
    build_historical_baseline,
    build_operator_acceptance,
    build_read_model,
    build_walk_forward_split,
)


def rights() -> DataRightsDeclaration:
    return DataRightsDeclaration(
        license_id="operator-owned-fixture",
        permitted_use="local-paper-research",
        retention_days=365,
    )


def observation(index: int, value: str, *, available_day: int | None = None):
    day = index
    available = day if available_day is None else available_day
    return HistoricalObservation(
        observation_id=f"obs.fixture.{index:03d}",
        instrument_id="instrument.fixture",
        field_id="field.fixture",
        event_at_utc=f"2026-01-{day:02d}T00:00:00Z",
        available_at_utc=f"2026-01-{available:02d}T01:00:00Z",
        value=Decimal(value),
        quality_status="registered-valid",
        source_id="operator-local-fixture",
        registered_artifact_id="artifact.fixture.history.v1",
        timezone_id="UTC",
        calendar_id="calendar.fixture.v1",
        adjustment_policy="none",
        missing_policy="abstain",
        duplicate_policy="reject",
        suspension_policy="preserve-missing",
        rights=rights(),
    )


def registry(*values: str) -> HistoricalObservationRegistry:
    result = HistoricalObservationRegistry()
    for index, value in enumerate(values, start=1):
        result = result.register(observation(index, value))
    return result


def request(**updates) -> BaselineRequest:
    values = {
        "request_id": "request.fixture.001",
        "instrument_id": "instrument.fixture",
        "field_id": "field.fixture",
        "as_of_utc": "2026-01-05T00:00:00Z",
        "window_size": 4,
        "minimum_history": 3,
    }
    values.update(updates)
    return BaselineRequest(**values)


def test_d1_boundary_and_data_rights_fail_closed():
    boundary = V2_R2_HISTORICAL_BASELINE_BOUNDARY
    assert boundary.registered_artifact_only is True
    assert boundary.operator_review_required is True
    assert boundary.remote_data_allowed is False
    assert boundary.factor_activation_allowed is False
    assert boundary.official_scoring_allowed is False
    assert boundary.order_path_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R2HistoricalBaselineBoundary(remote_data_allowed=True)
    with pytest.raises(ValueError, match="local data rights"):
        replace(rights(), operator_confirmed=False)
    with pytest.raises(ValueError, match="denies historical research"):
        replace(rights(), permitted_use="DENIED")


def test_d2_observation_is_immutable_and_blocks_time_travel():
    item = observation(1, "1")
    with pytest.raises(FrozenInstanceError):
        item.value = Decimal("2")
    with pytest.raises(ValueError, match="cannot precede"):
        replace(item, available_at_utc="2025-12-31T00:00:00Z")
    with pytest.raises(ValueError, match="missing_policy"):
        replace(item, missing_policy="silently-fill")


def test_d2_registry_rejects_duplicate_id_and_natural_key():
    item = observation(1, "1")
    with pytest.raises(ValueError, match="ids must be unique"):
        HistoricalObservationRegistry((item, item))
    with pytest.raises(ValueError, match="duplicate instrument"):
        HistoricalObservationRegistry(
            (item, replace(item, observation_id="obs.fixture.other"))
        )


def test_d3_baseline_is_deterministic_and_uses_prior_available_data_only():
    source = registry("1", "2", "3", "4", "100")
    first = build_historical_baseline(source, request())
    second = build_historical_baseline(source, request())
    assert first.status == "READY"
    assert first.observation_ids == (
        "obs.fixture.001",
        "obs.fixture.002",
        "obs.fixture.003",
        "obs.fixture.004",
    )
    assert first.mean == Decimal("2.5")
    assert first.variance == Decimal("1.25")
    assert first.replay_hash == second.replay_hash
    assert first.quantile_values["0.5"] == Decimal("2")


def test_d3_insufficient_history_and_zero_variance_abstain():
    insufficient = build_historical_baseline(registry("1", "2"), request())
    zero = build_historical_baseline(
        registry("5", "5", "5", "5"), request()
    )
    assert insufficient.status == "INSUFFICIENT_HISTORY"
    assert insufficient.standardize("3") == ("INSUFFICIENT_HISTORY", None)
    assert zero.standardize("5") == ("ZERO_VARIANCE", None)


def test_d3_standardization_is_decimal_and_reproducible():
    baseline = build_historical_baseline(registry("1", "2", "3", "4"), request())
    status, value = baseline.standardize("4")
    assert status == "READY"
    assert value is not None
    assert value == (Decimal("4") - baseline.mean) / baseline.standard_deviation


def test_d4_walk_forward_split_blocks_future_availability_leakage():
    late = observation(2, "2", available_day=5)
    source = HistoricalObservationRegistry((observation(1, "1"), late, observation(3, "3")))
    split = build_walk_forward_split(
        source,
        evaluation_start_utc="2026-01-03T00:00:00Z",
        as_of_utc="2026-01-06T00:00:00Z",
    )
    assert split.training_ids == ("obs.fixture.001",)
    assert split.evaluation_ids == ("obs.fixture.003",)
    assert "obs.fixture.002" not in split.training_ids


def test_d5_read_model_is_immutable_and_has_no_action_surface():
    baseline = build_historical_baseline(registry("1", "2", "3", "4"), request())
    payload = build_read_model(baseline).payload
    assert isinstance(payload, MappingProxyType)
    assert payload["read_only"] is True
    assert payload["operator_review_required"] is True
    assert payload["factor_activation_allowed"] is False
    assert payload["official_scoring_allowed"] is False
    assert payload["candidate_ranking_allowed"] is False
    assert payload["order_path_allowed"] is False
    with pytest.raises(TypeError):
        payload["status"] = "changed"


def test_d6_acceptance_requires_ready_baseline_and_operator_review():
    ready = build_operator_acceptance(
        build_historical_baseline(registry("1", "2", "3", "4"), request())
    )
    blocked = build_operator_acceptance(
        build_historical_baseline(registry("1"), request())
    )
    assert ready.status == "READY_FOR_OPERATOR_REVIEW"
    assert ready.operator_review_required is True
    assert ready.automatic_approval_allowed is False
    assert blocked.status == "BLOCKED"
