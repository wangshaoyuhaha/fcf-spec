from dataclasses import FrozenInstanceError
from decimal import Decimal
from types import MappingProxyType

import pytest

from apps.v2_r11_local_factor_registry_foundation_app_1 import (
    FactorDefinition,
    FactorRegistryPolicy,
    build_factor_registry,
)
from apps.v2_r12_local_technical_indicator_foundation_app_1 import (
    RegisteredPricePoint,
    RegisteredPriceSeries,
)
from apps.v2_r19_local_percentage_price_oscillator_foundation_app_1 import (
    V2_R19_PERCENTAGE_OSCILLATOR_BOUNDARY,
    PercentageOscillatorLedger,
    PercentageOscillatorPolicy,
    V2R19PercentageOscillatorBoundary,
    build_operator_acceptance,
    build_percentage_oscillator,
    build_read_model,
)


def _registry():
    definition = FactorDefinition(
        "registered-ppo",
        "v1",
        "TECHNICAL",
        "RESEARCH",
        "DETERMINISTIC_CODE",
        "e" * 64,
        "price",
        ("equity",),
        ("close",),
        minimum_lookback=4,
        maximum_lookback=200,
    )
    return build_factor_registry(
        (definition,),
        FactorRegistryPolicy("registered-factor-registry", "v1"),
        as_of_utc="2026-01-08T01:00:00Z",
    )


def _series(values: tuple[object, ...]) -> RegisteredPriceSeries:
    points = tuple(
        RegisteredPricePoint(
            point_id=f"registered-ppo-point-{index}",
            instrument_id="registered-equity",
            interval_id="registered-daily",
            observed_at_utc=f"2026-01-0{index}T00:00:00Z",
            available_at_utc=f"2026-01-0{index}T00:00:01Z",
            close=Decimal(str(value)),
            source_artifact_hash=format(index, "x") * 64,
        )
        for index, value in enumerate(values, start=1)
    )
    return RegisteredPriceSeries("registered-ppo-series", points)


def _policy(**changes: object) -> PercentageOscillatorPolicy:
    data: dict[str, object] = {
        "indicator_id": "registered-ppo",
        "indicator_version": "v1",
        "indicator_type": "PPO",
        "factor_definition_ref": "registered-ppo@v1",
        "registry_id": "registered-factor-registry",
        "registry_version": "v1",
        "instrument_id": "registered-equity",
        "interval_id": "registered-daily",
        "fast_window": 2,
        "slow_window": 3,
        "signal_window": 2,
        "decimal_places": 4,
    }
    data.update(changes)
    return PercentageOscillatorPolicy(**data)  # type: ignore[arg-type]


def _build(values: tuple[object, ...] = (10, 12, 11, 15), **changes: object):
    return build_percentage_oscillator(
        changes.get("series", _series(values)),  # type: ignore[arg-type]
        changes.get("registry", _registry()),  # type: ignore[arg-type]
        changes.get("policy", _policy()),  # type: ignore[arg-type]
        as_of_utc=str(changes.get("as_of_utc", "2026-01-08T01:00:00Z")),
    )


def test_d1_boundary_is_closed_and_immutable() -> None:
    assert V2_R19_PERCENTAGE_OSCILLATOR_BOUNDARY.threshold_or_crossover_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R19PercentageOscillatorBoundary(threshold_or_crossover_allowed=True)
    with pytest.raises(FrozenInstanceError):
        V2_R19_PERCENTAGE_OSCILLATOR_BOUNDARY.network_access_allowed = True  # type: ignore[misc]


def test_d2_policy_rejects_labels_signals_and_invalid_windows() -> None:
    with pytest.raises(ValueError, match="metric-only"):
        _policy(direction_label_allowed=True)
    with pytest.raises(ValueError, match="less than"):
        _policy(fast_window=3)


def test_d3_ppo_metrics_are_exact_and_deterministic() -> None:
    evidence = _build()
    assert evidence.ppo_line == Decimal("5.4131")
    assert evidence.signal_line == Decimal("3.9454")
    assert evidence.histogram == Decimal("1.4677")
    assert evidence.evidence_hash == _build().evidence_hash


def test_d3_constant_history_has_explicit_zero_metrics() -> None:
    evidence = _build((10, 10, 10, 10))
    assert evidence.ppo_line == Decimal("0.0000")
    assert evidence.signal_line == Decimal("0.0000")
    assert evidence.histogram == Decimal("0.0000")


def test_d4_insufficient_history_is_blocked() -> None:
    evidence = _build((10, 12, 11))
    assert evidence.required_samples == 4
    assert evidence.reason_codes == ("INSUFFICIENT_WINDOW_BLOCKED",)


def test_d4_future_availability_is_blocked() -> None:
    series = _series((10, 12, 11, 15))
    last = series.points[-1]
    future = RegisteredPricePoint(
        point_id=last.point_id,
        instrument_id=last.instrument_id,
        interval_id=last.interval_id,
        observed_at_utc=last.observed_at_utc,
        available_at_utc="2026-01-09T00:00:00Z",
        close=last.close,
        source_artifact_hash=last.source_artifact_hash,
    )
    evidence = _build(
        series=RegisteredPriceSeries(series.series_id, (*series.points[:-1], future))
    )
    assert evidence.reason_codes == ("FUTURE_AVAILABILITY_BLOCKED",)


def test_d4_registry_factor_and_series_identity_are_required() -> None:
    wrong_registry = _build(policy=_policy(registry_version="v2"))
    missing_factor = _build(policy=_policy(factor_definition_ref="missing@v1"))
    wrong_series = _build(policy=_policy(instrument_id="registered-btc"))
    assert wrong_registry.reason_codes == ("REGISTRY_IDENTITY_MISMATCH",)
    assert missing_factor.reason_codes == ("FACTOR_DEFINITION_NOT_REGISTERED",)
    assert wrong_series.reason_codes == ("SERIES_IDENTITY_MISMATCH",)


def test_d5_ledger_rejects_duplicate_and_invalid_capacity() -> None:
    evidence = _build()
    ledger = PercentageOscillatorLedger().append(evidence)
    with pytest.raises(ValueError, match="duplicate"):
        ledger.append(evidence)
    with pytest.raises(ValueError, match="capacity"):
        PercentageOscillatorLedger(capacity=0)


def test_d6_read_model_and_acceptance_are_non_activating() -> None:
    evidence = _build()
    model = build_read_model(PercentageOscillatorLedger().append(evidence))
    acceptance = build_operator_acceptance(evidence)
    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["direction_label"] is False
    assert model.payload["threshold_or_crossover"] is False
    assert model.payload["order_or_execution"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    assert acceptance.signal_or_recommendation_allowed is False
