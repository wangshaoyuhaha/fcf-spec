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
    RegisteredOHLCPoint,
    RegisteredOHLCSeries,
)
from apps.v2_r17_local_stochastic_oscillator_foundation_app_1 import (
    V2_R17_STOCHASTIC_INDICATOR_BOUNDARY,
    StochasticIndicatorLedger,
    StochasticIndicatorPolicy,
    V2R17StochasticIndicatorBoundary,
    build_operator_acceptance,
    build_read_model,
    build_stochastic_indicator,
)


def _registry():
    definition = FactorDefinition(
        "registered-stochastic",
        "v1",
        "TECHNICAL",
        "RESEARCH",
        "DETERMINISTIC_CODE",
        "e" * 64,
        "price",
        ("equity",),
        ("close", "high", "low"),
        minimum_lookback=2,
        maximum_lookback=200,
    )
    return build_factor_registry(
        (definition,),
        FactorRegistryPolicy("registered-factor-registry", "v1"),
        as_of_utc="2026-01-08T01:00:00Z",
    )


def _series(
    values: tuple[tuple[object, object, object, object], ...],
) -> RegisteredOHLCSeries:
    points = tuple(
        RegisteredOHLCPoint(
            point_id=f"registered-stochastic-point-{index}",
            instrument_id="registered-equity",
            interval_id="registered-daily",
            observed_at_utc=f"2026-01-0{index}T00:00:00Z",
            available_at_utc=f"2026-01-0{index}T00:00:01Z",
            open=Decimal(str(value[0])),
            high=Decimal(str(value[1])),
            low=Decimal(str(value[2])),
            close=Decimal(str(value[3])),
            source_artifact_hash=format(index, "x") * 64,
        )
        for index, value in enumerate(values, start=1)
    )
    return RegisteredOHLCSeries("registered-stochastic-series", points)


def _policy(**changes: object) -> StochasticIndicatorPolicy:
    data: dict[str, object] = {
        "indicator_id": "registered-kdj",
        "indicator_version": "v1",
        "indicator_type": "KDJ",
        "factor_definition_ref": "registered-stochastic@v1",
        "registry_id": "registered-factor-registry",
        "registry_version": "v1",
        "instrument_id": "registered-equity",
        "interval_id": "registered-daily",
        "window": 3,
        "smoothing_period": 3,
        "seed": Decimal("50"),
        "decimal_places": 4,
    }
    data.update(changes)
    return StochasticIndicatorPolicy(**data)  # type: ignore[arg-type]


def _build(
    values: tuple[tuple[object, object, object, object], ...] = (
        (9, 10, 8, 9),
        (10, 12, 9, 11),
        (12, 14, 10, 13),
        (13, 15, 11, 14),
    ),
    **changes: object,
):
    return build_stochastic_indicator(
        changes.get("series", _series(values)),  # type: ignore[arg-type]
        changes.get("registry", _registry()),  # type: ignore[arg-type]
        changes.get("policy", _policy()),  # type: ignore[arg-type]
        as_of_utc=str(changes.get("as_of_utc", "2026-01-08T01:00:00Z")),
    )


def test_d1_boundary_is_closed_and_immutable() -> None:
    assert V2_R17_STOCHASTIC_INDICATOR_BOUNDARY.threshold_or_crossover_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R17StochasticIndicatorBoundary(threshold_or_crossover_allowed=True)
    with pytest.raises(FrozenInstanceError):
        V2_R17_STOCHASTIC_INDICATOR_BOUNDARY.network_access_allowed = True  # type: ignore[misc]


def test_d2_policy_rejects_signals_and_invalid_parameters() -> None:
    with pytest.raises(ValueError, match="metric-only"):
        _policy(threshold_or_crossover_allowed=True)
    with pytest.raises(ValueError, match="window"):
        _policy(window=1)
    with pytest.raises(ValueError, match="smoothing"):
        _policy(smoothing_period=1)
    with pytest.raises(ValueError, match="seed"):
        _policy(seed=Decimal("101"))


def test_d3_kdj_metrics_are_exact_recursive_and_deterministic() -> None:
    evidence = _build()
    assert evidence.rsv == Decimal("83.3333")
    assert evidence.k_value == Decimal("68.5185")
    assert evidence.d_value == Decimal("58.6420")
    assert evidence.j_value == Decimal("88.2716")
    assert evidence.evidence_hash == _build().evidence_hash


def test_d3_flat_window_has_explicit_neutral_metrics() -> None:
    evidence = _build(((10, 10, 10, 10),) * 3)
    assert evidence.rsv == Decimal("50.0000")
    assert evidence.k_value == Decimal("50.0000")
    assert evidence.d_value == Decimal("50.0000")
    assert evidence.j_value == Decimal("50.0000")


def test_d4_insufficient_window_is_blocked() -> None:
    evidence = _build(((9, 10, 8, 9), (10, 12, 9, 11)))
    assert evidence.reason_codes == ("INSUFFICIENT_WINDOW_BLOCKED",)


def test_d4_future_availability_is_blocked() -> None:
    series = _series(((9, 10, 8, 9), (10, 12, 9, 11), (12, 14, 10, 13)))
    last = series.points[-1]
    future = RegisteredOHLCPoint(
        point_id=last.point_id,
        instrument_id=last.instrument_id,
        interval_id=last.interval_id,
        observed_at_utc=last.observed_at_utc,
        available_at_utc="2026-01-09T00:00:00Z",
        open=last.open,
        high=last.high,
        low=last.low,
        close=last.close,
        source_artifact_hash=last.source_artifact_hash,
    )
    evidence = _build(
        series=RegisteredOHLCSeries(series.series_id, (*series.points[:-1], future))
    )
    assert evidence.reason_codes == ("FUTURE_AVAILABILITY_BLOCKED",)


def test_d4_registry_factor_and_series_identity_are_required() -> None:
    wrong_registry = _build(policy=_policy(registry_version="v2"))
    missing_factor = _build(
        policy=_policy(factor_definition_ref="registered-missing@v1")
    )
    wrong_series = _build(policy=_policy(instrument_id="registered-btc"))
    assert wrong_registry.reason_codes == ("REGISTRY_IDENTITY_MISMATCH",)
    assert missing_factor.reason_codes == ("FACTOR_DEFINITION_NOT_REGISTERED",)
    assert wrong_series.reason_codes == ("SERIES_IDENTITY_MISMATCH",)


def test_d5_ledger_rejects_duplicate_and_invalid_capacity() -> None:
    evidence = _build()
    ledger = StochasticIndicatorLedger().append(evidence)
    with pytest.raises(ValueError, match="duplicate"):
        ledger.append(evidence)
    with pytest.raises(ValueError, match="capacity"):
        StochasticIndicatorLedger(capacity=0)


def test_d6_read_model_and_acceptance_are_non_activating() -> None:
    evidence = _build()
    model = build_read_model(StochasticIndicatorLedger().append(evidence))
    acceptance = build_operator_acceptance(evidence)
    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["threshold_label"] is False
    assert model.payload["crossover"] is False
    assert model.payload["order_or_execution"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    assert acceptance.signal_or_recommendation_allowed is False
