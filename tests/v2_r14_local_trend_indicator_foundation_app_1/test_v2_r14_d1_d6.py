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
from apps.v2_r14_local_trend_indicator_foundation_app_1 import (
    V2_R14_TREND_INDICATOR_BOUNDARY,
    TrendIndicatorLedger,
    TrendIndicatorPolicy,
    V2R14TrendIndicatorBoundary,
    build_operator_acceptance,
    build_read_model,
    build_trend_indicator,
)


def _registry():
    definition = FactorDefinition(
        "registered-trend",
        "v1",
        "TECHNICAL",
        "RESEARCH",
        "DETERMINISTIC_CODE",
        "c" * 64,
        "price",
        ("equity",),
        ("close",),
        minimum_lookback=2,
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
            point_id=f"registered-point-{index}",
            instrument_id="registered-equity",
            interval_id="registered-daily",
            observed_at_utc=f"2026-01-0{index}T00:00:00Z",
            available_at_utc=f"2026-01-0{index}T00:00:01Z",
            close=Decimal(str(value)),
            source_artifact_hash=format(index, "x") * 64,
        )
        for index, value in enumerate(values, start=1)
    )
    return RegisteredPriceSeries("registered-trend-series", points)


def _policy(**changes: object) -> TrendIndicatorPolicy:
    data: dict[str, object] = {
        "indicator_id": "registered-ema",
        "indicator_version": "v1",
        "indicator_type": "EMA",
        "factor_definition_ref": "registered-trend@v1",
        "registry_id": "registered-factor-registry",
        "registry_version": "v1",
        "instrument_id": "registered-equity",
        "interval_id": "registered-daily",
        "fast_window": 3,
        "slow_window": 5,
        "signal_window": 2,
        "decimal_places": 4,
    }
    data.update(changes)
    return TrendIndicatorPolicy(**data)  # type: ignore[arg-type]


def _build(values: tuple[object, ...] = (1, 2, 3), **changes: object):
    return build_trend_indicator(
        changes.get("series", _series(values)),  # type: ignore[arg-type]
        changes.get("registry", _registry()),  # type: ignore[arg-type]
        changes.get("policy", _policy()),  # type: ignore[arg-type]
        as_of_utc=str(changes.get("as_of_utc", "2026-01-08T01:00:00Z")),
    )


def test_d1_boundary_is_closed_and_immutable() -> None:
    assert V2_R14_TREND_INDICATOR_BOUNDARY.prediction_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R14TrendIndicatorBoundary(score_rank_or_signal_allowed=True)
    with pytest.raises(FrozenInstanceError):
        V2_R14_TREND_INDICATOR_BOUNDARY.network_access_allowed = True  # type: ignore[misc]


def test_d2_policy_rejects_signal_and_invalid_windows() -> None:
    with pytest.raises(ValueError, match="calculation-only"):
        _policy(score_rank_or_signal_allowed=True)
    with pytest.raises(ValueError, match="fast_window"):
        _policy(fast_window=1)
    with pytest.raises(ValueError, match="less than"):
        _policy(indicator_type="MACD", fast_window=5, slow_window=5)
    with pytest.raises(ValueError, match="warm-up"):
        _policy(indicator_type="MACD", slow_window=9999, signal_window=3)


def test_d3_ema_is_seeded_exact_and_deterministic() -> None:
    evidence = _build()
    assert evidence.state == "TREND_READY"
    assert evidence.ema == Decimal("2.2500")
    assert evidence.evidence_hash == _build().evidence_hash


def test_d3_macd_lines_are_exact_after_explicit_warmup() -> None:
    evidence = _build(
        (1, 2, 3, 4),
        policy=_policy(
            indicator_id="registered-macd",
            indicator_type="MACD",
            fast_window=2,
            slow_window=3,
            signal_window=2,
        ),
    )
    assert evidence.required_samples == 4
    assert evidence.macd_line == Decimal("0.3935")
    assert evidence.signal_line == Decimal("0.3642")
    assert evidence.histogram == Decimal("0.0293")
    assert evidence.ema is None


@pytest.mark.parametrize(
    ("policy", "values"),
    [
        (_policy(), (1, 2)),
        (
            _policy(
                indicator_type="MACD",
                fast_window=2,
                slow_window=3,
                signal_window=2,
            ),
            (1, 2, 3),
        ),
    ],
)
def test_d4_insufficient_warmup_is_blocked(
    policy: TrendIndicatorPolicy, values: tuple[object, ...]
) -> None:
    evidence = _build(series=_series(values), policy=policy)
    assert evidence.reason_codes == ("INSUFFICIENT_WINDOW_BLOCKED",)


def test_d4_future_availability_is_blocked() -> None:
    series = _series((1, 2, 3))
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


def test_d4_registry_and_factor_identity_are_required() -> None:
    wrong_registry = _build(policy=_policy(registry_version="v2"))
    missing_factor = _build(
        policy=_policy(factor_definition_ref="registered-missing@v1")
    )
    assert wrong_registry.reason_codes == ("REGISTRY_IDENTITY_MISMATCH",)
    assert missing_factor.reason_codes == ("FACTOR_DEFINITION_NOT_REGISTERED",)


def test_d5_ledger_rejects_duplicate_and_invalid_capacity() -> None:
    evidence = _build()
    ledger = TrendIndicatorLedger().append(evidence)
    with pytest.raises(ValueError, match="duplicate"):
        ledger.append(evidence)
    with pytest.raises(ValueError, match="capacity"):
        TrendIndicatorLedger(capacity=0)


def test_d6_read_model_and_acceptance_are_non_activating() -> None:
    evidence = _build()
    model = build_read_model(TrendIndicatorLedger().append(evidence))
    acceptance = build_operator_acceptance(evidence)
    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["score_rank_or_signal"] is False
    assert model.payload["order_or_execution"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    assert acceptance.signal_or_recommendation_allowed is False
