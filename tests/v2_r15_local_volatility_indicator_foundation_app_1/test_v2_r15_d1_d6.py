from dataclasses import FrozenInstanceError
from decimal import Decimal
from types import MappingProxyType

import pytest

from apps.v2_r11_local_factor_registry_foundation_app_1 import (
    FactorDefinition,
    FactorRegistryPolicy,
    build_factor_registry,
)
from apps.v2_r15_local_volatility_indicator_foundation_app_1 import (
    V2_R15_VOLATILITY_INDICATOR_BOUNDARY,
    RegisteredOHLCPoint,
    RegisteredOHLCSeries,
    V2R15VolatilityIndicatorBoundary,
    VolatilityIndicatorLedger,
    VolatilityIndicatorPolicy,
    build_operator_acceptance,
    build_read_model,
    build_volatility_indicator,
)


def _registry():
    definition = FactorDefinition(
        "registered-volatility",
        "v1",
        "TECHNICAL",
        "RESEARCH",
        "DETERMINISTIC_CODE",
        "d" * 64,
        "price",
        ("equity",),
        ("close", "high", "low", "open"),
        minimum_lookback=2,
        maximum_lookback=200,
    )
    return build_factor_registry(
        (definition,),
        FactorRegistryPolicy("registered-factor-registry", "v1"),
        as_of_utc="2026-01-08T01:00:00Z",
    )


def _point(
    index: int,
    values: tuple[object, object, object, object],
    *,
    available_at_utc: str | None = None,
) -> RegisteredOHLCPoint:
    open_value, high, low, close = values
    return RegisteredOHLCPoint(
        point_id=f"registered-ohlc-{index}",
        instrument_id="registered-equity",
        interval_id="registered-daily",
        observed_at_utc=f"2026-01-0{index}T00:00:00Z",
        available_at_utc=available_at_utc or f"2026-01-0{index}T00:00:01Z",
        open=Decimal(str(open_value)),
        high=Decimal(str(high)),
        low=Decimal(str(low)),
        close=Decimal(str(close)),
        source_artifact_hash=format(index, "x") * 64,
    )


def _series(
    values: tuple[tuple[object, object, object, object], ...],
) -> RegisteredOHLCSeries:
    return RegisteredOHLCSeries(
        "registered-volatility-series",
        tuple(_point(index, value) for index, value in enumerate(values, start=1)),
    )


def _policy(**changes: object) -> VolatilityIndicatorPolicy:
    data: dict[str, object] = {
        "indicator_id": "registered-atr",
        "indicator_version": "v1",
        "indicator_type": "AVERAGE_TRUE_RANGE",
        "factor_definition_ref": "registered-volatility@v1",
        "registry_id": "registered-factor-registry",
        "registry_version": "v1",
        "instrument_id": "registered-equity",
        "interval_id": "registered-daily",
        "window": 3,
        "decimal_places": 4,
    }
    data.update(changes)
    return VolatilityIndicatorPolicy(**data)  # type: ignore[arg-type]


def _build(
    values: tuple[tuple[object, object, object, object], ...] = (
        (9, 10, 8, 9),
        (10, 12, 9, 11),
        (12, 14, 10, 13),
    ),
    **changes: object,
):
    return build_volatility_indicator(
        changes.get("series", _series(values)),  # type: ignore[arg-type]
        changes.get("registry", _registry()),  # type: ignore[arg-type]
        changes.get("policy", _policy()),  # type: ignore[arg-type]
        as_of_utc=str(changes.get("as_of_utc", "2026-01-08T01:00:00Z")),
    )


def test_d1_boundary_is_closed_and_immutable() -> None:
    assert V2_R15_VOLATILITY_INDICATOR_BOUNDARY.prediction_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R15VolatilityIndicatorBoundary(score_rank_or_signal_allowed=True)
    with pytest.raises(FrozenInstanceError):
        V2_R15_VOLATILITY_INDICATOR_BOUNDARY.network_access_allowed = True  # type: ignore[misc]


def test_d2_ohlc_contract_rejects_invalid_bounds() -> None:
    with pytest.raises(ValueError, match="open must be within"):
        _point(1, (11, 10, 8, 9))
    with pytest.raises(ValueError, match="close must be within"):
        _point(1, (9, 10, 8, 11))


def test_d2_policy_rejects_signal_and_invalid_window() -> None:
    with pytest.raises(ValueError, match="calculation-only"):
        _policy(score_rank_or_signal_allowed=True)
    with pytest.raises(ValueError, match="window"):
        _policy(window=1)


def test_d3_true_range_uses_previous_close_gap() -> None:
    evidence = _build(
        ((9, 10, 8, 9), (11, 12, 10, 11)),
        policy=_policy(indicator_type="TRUE_RANGE"),
    )
    assert evidence.true_range == Decimal("3.0000")
    assert evidence.average_true_range is None


def test_d3_first_true_range_is_high_minus_low() -> None:
    evidence = _build(
        ((9, 10, 8, 9),), policy=_policy(indicator_type="TRUE_RANGE")
    )
    assert evidence.true_range == Decimal("2.0000")


def test_d3_wilder_atr_seed_and_recursion_are_exact_and_deterministic() -> None:
    values = (
        (9, 10, 8, 9),
        (10, 12, 9, 11),
        (12, 14, 10, 13),
        (14, 18, 12, 17),
    )
    evidence = _build(values)
    assert evidence.average_true_range == Decimal("4.0000")
    assert evidence.evidence_hash == _build(values).evidence_hash


def test_d4_insufficient_atr_window_is_blocked() -> None:
    evidence = _build(((9, 10, 8, 9), (10, 12, 9, 11)))
    assert evidence.reason_codes == ("INSUFFICIENT_WINDOW_BLOCKED",)


def test_d4_future_availability_is_blocked() -> None:
    series = _series(((9, 10, 8, 9), (10, 12, 9, 11), (12, 14, 10, 13)))
    future = _point(3, (12, 14, 10, 13), available_at_utc="2026-01-09T00:00:00Z")
    evidence = _build(
        series=RegisteredOHLCSeries(series.series_id, (*series.points[:-1], future))
    )
    assert evidence.reason_codes == ("FUTURE_AVAILABILITY_BLOCKED",)


def test_d4_registry_and_factor_identity_are_required() -> None:
    wrong_registry = _build(policy=_policy(registry_version="v2"))
    missing_factor = _build(
        policy=_policy(factor_definition_ref="registered-missing@v1")
    )
    assert wrong_registry.reason_codes == ("REGISTRY_IDENTITY_MISMATCH",)
    assert missing_factor.reason_codes == ("FACTOR_DEFINITION_NOT_REGISTERED",)


def test_d5_ledger_rejects_duplicate_and_invalid_capacity() -> None:
    evidence = _build()
    ledger = VolatilityIndicatorLedger().append(evidence)
    with pytest.raises(ValueError, match="duplicate"):
        ledger.append(evidence)
    with pytest.raises(ValueError, match="capacity"):
        VolatilityIndicatorLedger(capacity=0)


def test_d6_read_model_and_acceptance_are_non_activating() -> None:
    evidence = _build()
    model = build_read_model(VolatilityIndicatorLedger().append(evidence))
    acceptance = build_operator_acceptance(evidence)
    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["score_rank_or_signal"] is False
    assert model.payload["order_or_execution"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    assert acceptance.signal_or_recommendation_allowed is False
