from dataclasses import FrozenInstanceError
from decimal import Decimal
from types import MappingProxyType

import pytest

from apps.v2_r11_local_factor_registry_foundation_app_1 import FactorDefinition, FactorRegistryPolicy, build_factor_registry
from apps.v2_r21_local_robust_normalization_foundation_app_1 import MISSING_STATES, V2_R21_NORMALIZATION_BOUNDARY, NormalizationLedger, NormalizationPolicy, RegisteredFactorPoint, RegisteredFactorSeries, V2R21NormalizationBoundary, build_normalization, build_operator_acceptance, build_read_model


def _registry():
    definition = FactorDefinition("registered-robust", "v1", "TECHNICAL", "RESEARCH", "DETERMINISTIC_CODE", "e" * 64, "factor-value", ("equity",), ("value",), minimum_lookback=3, maximum_lookback=200)
    return build_factor_registry((definition,), FactorRegistryPolicy("registered-factor-registry", "v1"), as_of_utc="2026-01-08T01:00:00Z")


def _series(values: tuple[object | None, ...], states: tuple[str, ...] | None = None) -> RegisteredFactorSeries:
    states = states or tuple("AVAILABLE" for _ in values)
    points = tuple(RegisteredFactorPoint(f"registered-factor-point-{index}", "registered-robust@v1", "registered-equity", f"2026-01-0{index}T00:00:00Z", f"2026-01-0{index}T00:00:01Z", None if value is None else Decimal(str(value)), state, format(index, "x") * 64) for index, (value, state) in enumerate(zip(values, states), start=1))
    return RegisteredFactorSeries("registered-factor-series", points)


def _policy(**changes: object) -> NormalizationPolicy:
    data: dict[str, object] = {"normalization_id": "registered-robust-normalization", "normalization_version": "v1", "factor_definition_ref": "registered-robust@v1", "registry_id": "registered-factor-registry", "registry_version": "v1", "target_point_id": "registered-factor-point-4", "minimum_samples": 4, "mad_clip_multiplier": Decimal("3"), "decimal_places": 4}
    data.update(changes); return NormalizationPolicy(**data)  # type: ignore[arg-type]


def _build(values: tuple[object | None, ...] = (1, 2, 3, 100), **changes: object):
    return build_normalization(changes.get("series", _series(values)), changes.get("registry", _registry()), changes.get("policy", _policy()), as_of_utc=str(changes.get("as_of_utc", "2026-01-08T01:00:00Z")))  # type: ignore[arg-type]


def test_d1_boundary_and_missing_taxonomy_are_closed() -> None:
    assert MISSING_STATES == ("AVAILABLE", "NOT_APPLICABLE", "NOT_YET_PUBLISHED", "MISSING", "SOURCE_FAILURE")
    with pytest.raises(ValueError, match="prohibited capability"): V2R21NormalizationBoundary(weight_score_rank_or_signal_allowed=True)
    with pytest.raises(FrozenInstanceError): V2_R21_NORMALIZATION_BOUNDARY.network_access_allowed = True  # type: ignore[misc]


def test_d2_contract_distinguishes_true_zero_from_missing() -> None:
    assert _series((0, 1, 2, 3)).points[0].value == Decimal(0)
    with pytest.raises(ValueError, match="cannot carry"): _series((1, None, 2), ("AVAILABLE", "MISSING", "AVAILABLE")).points[1].__class__("bad", "registered-robust@v1", "registered-equity", "2026-01-04T00:00:00Z", "2026-01-04T00:00:01Z", Decimal(0), "MISSING", "a" * 64)
    with pytest.raises(ValueError, match="metric-only"): _policy(direction_weight_score_rank_allowed=True)


def test_d3_robust_metrics_are_exact_and_deterministic() -> None:
    evidence = _build()
    assert evidence.median == Decimal("2.5000")
    assert evidence.mad == Decimal("1.0000")
    assert evidence.winsorized_value == Decimal("5.5000")
    assert evidence.robust_z_score == Decimal("3.0000")
    assert evidence.evidence_hash == _build().evidence_hash


def test_d3_flat_history_has_explicit_zero_robust_z() -> None:
    evidence = _build((7, 7, 7, 7))
    assert evidence.mad == Decimal("0.0000")
    assert evidence.robust_z_score == Decimal("0.0000")


def test_d4_missing_target_is_recorded_without_zero_fill() -> None:
    series = _series((1, 2, 3, 4, None), ("AVAILABLE", "AVAILABLE", "AVAILABLE", "AVAILABLE", "NOT_YET_PUBLISHED"))
    evidence = _build(series=series, policy=_policy(target_point_id="registered-factor-point-5"))
    assert evidence.state == "MISSING_STATE_RECORDED"
    assert evidence.missing_state == "NOT_YET_PUBLISHED"
    assert evidence.robust_z_score is None


def test_d4_insufficient_and_future_are_blocked() -> None:
    assert _build((1, 2, 3), policy=_policy(target_point_id="registered-factor-point-3")).reason_codes == ("INSUFFICIENT_AVAILABLE_SAMPLES",)
    series = _series((1, 2, 3, 4)); last = series.points[-1]
    future = RegisteredFactorPoint(last.point_id, last.factor_definition_ref, last.instrument_id, last.observed_at_utc, "2026-01-09T00:00:00Z", last.value, last.missing_state, last.source_artifact_hash)
    assert _build(series=RegisteredFactorSeries(series.series_id, (*series.points[:-1], future))).reason_codes == ("FUTURE_AVAILABILITY_BLOCKED",)


def test_d4_registry_factor_and_target_identity_are_required() -> None:
    assert _build(policy=_policy(registry_version="v2")).reason_codes == ("REGISTRY_IDENTITY_MISMATCH",)
    assert _build(policy=_policy(factor_definition_ref="missing@v1")).reason_codes == ("FACTOR_DEFINITION_NOT_REGISTERED",)
    assert _build(policy=_policy(target_point_id="missing-point")).reason_codes == ("TARGET_POINT_NOT_REGISTERED",)


def test_d5_ledger_rejects_duplicate_and_invalid_capacity() -> None:
    evidence = _build(); ledger = NormalizationLedger().append(evidence)
    with pytest.raises(ValueError, match="duplicate"): ledger.append(evidence)
    with pytest.raises(ValueError, match="capacity"): NormalizationLedger(capacity=0)


def test_d6_read_model_and_acceptance_are_non_activating() -> None:
    evidence = _build(); model = build_read_model(NormalizationLedger().append(evidence)); acceptance = build_operator_acceptance(evidence)
    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["direction_weight_score_rank"] is False
    assert model.payload["order_or_execution"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    assert acceptance.score_rank_or_recommendation_allowed is False
