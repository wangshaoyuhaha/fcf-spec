from dataclasses import FrozenInstanceError
from decimal import Decimal
from types import MappingProxyType

import pytest

from apps.v2_r11_local_factor_registry_foundation_app_1 import FactorDefinition, FactorRegistryPolicy, build_factor_registry
from apps.v2_r12_local_technical_indicator_foundation_app_1 import (
    V2_R12_TECHNICAL_INDICATOR_BOUNDARY,
    RegisteredPricePoint,
    RegisteredPriceSeries,
    TechnicalIndicatorLedger,
    TechnicalIndicatorPolicy,
    V2R12TechnicalIndicatorBoundary,
    build_operator_acceptance,
    build_read_model,
    build_technical_indicator,
)


def _registry():
    definition = FactorDefinition("registered-close-ma", "v1", "TECHNICAL", "RESEARCH", "DETERMINISTIC_CODE", "a" * 64, "price", ("equity",), ("close",), minimum_lookback=2, maximum_lookback=200)
    return build_factor_registry((definition,), FactorRegistryPolicy("registered-factor-registry", "v1"), as_of_utc="2026-01-05T01:06:00Z")


def _point(index: int, **changes: object) -> RegisteredPricePoint:
    data: dict[str, object] = dict(point_id=f"registered-point-{index}", instrument_id="registered-equity", interval_id="registered-daily", observed_at_utc=f"2026-01-0{index}T00:00:00Z", available_at_utc=f"2026-01-0{index}T00:00:01Z", close=Decimal(index), source_artifact_hash=f"{index}" * 64)
    data.update(changes)
    return RegisteredPricePoint(**data)  # type: ignore[arg-type]


def _series(count: int = 4) -> RegisteredPriceSeries:
    return RegisteredPriceSeries("registered-price-series", tuple(_point(index) for index in range(1, count + 1)))


def _policy(**changes: object) -> TechnicalIndicatorPolicy:
    data: dict[str, object] = dict(indicator_id="registered-sma", indicator_version="v1", indicator_type="SMA", factor_definition_ref="registered-close-ma@v1", registry_id="registered-factor-registry", registry_version="v1", instrument_id="registered-equity", interval_id="registered-daily", window=4, decimal_places=4)
    data.update(changes)
    return TechnicalIndicatorPolicy(**data)  # type: ignore[arg-type]


def _build(**changes: object):
    return build_technical_indicator(changes.get("series", _series()), changes.get("registry", _registry()), changes.get("policy", _policy()), as_of_utc=str(changes.get("as_of_utc", "2026-01-05T01:06:00Z")))  # type: ignore[arg-type]


def test_d1_boundary_is_closed_and_immutable() -> None:
    assert V2_R12_TECHNICAL_INDICATOR_BOUNDARY.prediction_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R12TechnicalIndicatorBoundary(score_rank_or_signal_allowed=True)
    with pytest.raises(FrozenInstanceError):
        V2_R12_TECHNICAL_INDICATOR_BOUNDARY.network_access_allowed = True  # type: ignore[misc]


def test_d2_series_rejects_unordered_or_mixed_identity() -> None:
    with pytest.raises(ValueError, match="ordered"):
        RegisteredPriceSeries("registered-series", (_point(2), _point(1)))
    with pytest.raises(ValueError, match="identity"):
        RegisteredPriceSeries("registered-series", (_point(1), _point(2, instrument_id="other-equity")))


def test_d2_policy_rejects_signal_and_invalid_window() -> None:
    with pytest.raises(ValueError, match="calculation-only"):
        _policy(score_rank_or_signal_allowed=True)
    with pytest.raises(ValueError, match="window"):
        _policy(window=1)


def test_d3_sma_is_exact_and_deterministic() -> None:
    evidence = _build()
    assert evidence.state == "INDICATOR_READY"
    assert evidence.sma == Decimal("2.5000")
    assert evidence.standard_deviation is None
    assert evidence.evidence_hash == _build().evidence_hash


def test_d3_bollinger_bands_use_population_standard_deviation() -> None:
    evidence = _build(policy=_policy(indicator_type="BOLLINGER_BANDS"))
    assert evidence.sma == Decimal("2.5000")
    assert evidence.standard_deviation == Decimal("1.1180")
    assert evidence.upper_band == Decimal("4.7361")
    assert evidence.lower_band == Decimal("0.2639")


def test_d4_insufficient_window_is_blocked() -> None:
    evidence = _build(series=_series(3))
    assert evidence.reason_codes == ("INSUFFICIENT_WINDOW_BLOCKED",)


def test_d4_future_availability_is_blocked() -> None:
    points = tuple(_point(index) for index in range(1, 4)) + (_point(4, available_at_utc="2026-01-06T00:00:00Z"),)
    evidence = _build(series=RegisteredPriceSeries("registered-series", points))
    assert evidence.reason_codes == ("FUTURE_AVAILABILITY_BLOCKED",)


def test_d4_registry_and_factor_identity_are_required() -> None:
    registry = _registry()
    wrong_registry = _build(policy=_policy(registry_version="v2"))
    missing_factor = _build(policy=_policy(factor_definition_ref="registered-missing@v1"))
    assert registry.state == "REGISTRY_READY"
    assert wrong_registry.reason_codes == ("REGISTRY_IDENTITY_MISMATCH",)
    assert missing_factor.reason_codes == ("FACTOR_DEFINITION_NOT_REGISTERED",)


def test_d5_ledger_rejects_duplicate_evidence() -> None:
    evidence = _build()
    ledger = TechnicalIndicatorLedger().append(evidence)
    with pytest.raises(ValueError, match="duplicate"):
        ledger.append(evidence)


def test_d5_ledger_capacity_is_bounded() -> None:
    with pytest.raises(ValueError, match="capacity"):
        TechnicalIndicatorLedger(capacity=0)


def test_d6_read_model_and_acceptance_are_non_activating() -> None:
    evidence = _build()
    model = build_read_model(TechnicalIndicatorLedger().append(evidence))
    acceptance = build_operator_acceptance(evidence)
    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["score_rank_or_signal"] is False
    assert model.payload["order_or_execution"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    assert acceptance.signal_or_recommendation_allowed is False
