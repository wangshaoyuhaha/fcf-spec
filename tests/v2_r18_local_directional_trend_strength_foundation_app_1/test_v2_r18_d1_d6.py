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
from apps.v2_r18_local_directional_trend_strength_foundation_app_1 import (
    V2_R18_DIRECTIONAL_STRENGTH_BOUNDARY,
    DirectionalStrengthLedger,
    DirectionalStrengthPolicy,
    V2R18DirectionalStrengthBoundary,
    build_directional_strength,
    build_operator_acceptance,
    build_read_model,
)


def _registry():
    definition = FactorDefinition(
        "registered-adx",
        "v1",
        "TECHNICAL",
        "RESEARCH",
        "DETERMINISTIC_CODE",
        "e" * 64,
        "price",
        ("equity",),
        ("close", "high", "low"),
        minimum_lookback=4,
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
            point_id=f"registered-adx-point-{index}",
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
    return RegisteredOHLCSeries("registered-adx-series", points)


def _policy(**changes: object) -> DirectionalStrengthPolicy:
    data: dict[str, object] = {
        "indicator_id": "registered-adx",
        "indicator_version": "v1",
        "indicator_type": "ADX",
        "factor_definition_ref": "registered-adx@v1",
        "registry_id": "registered-factor-registry",
        "registry_version": "v1",
        "instrument_id": "registered-equity",
        "interval_id": "registered-daily",
        "window": 2,
        "decimal_places": 4,
    }
    data.update(changes)
    return DirectionalStrengthPolicy(**data)  # type: ignore[arg-type]


def _build(
    values: tuple[tuple[object, object, object, object], ...] = (
        (9, 10, 8, 9),
        (10, 12, 9, 11),
        (11, 13, 10, 12),
        (10, 12, 8, 9),
        (8, 11, 7, 8),
    ),
    **changes: object,
):
    return build_directional_strength(
        changes.get("series", _series(values)),  # type: ignore[arg-type]
        changes.get("registry", _registry()),  # type: ignore[arg-type]
        changes.get("policy", _policy()),  # type: ignore[arg-type]
        as_of_utc=str(changes.get("as_of_utc", "2026-01-08T01:00:00Z")),
    )


def test_d1_boundary_is_closed_and_immutable() -> None:
    assert V2_R18_DIRECTIONAL_STRENGTH_BOUNDARY.trend_label_or_direction_claim_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R18DirectionalStrengthBoundary(trend_label_or_direction_claim_allowed=True)
    with pytest.raises(FrozenInstanceError):
        V2_R18_DIRECTIONAL_STRENGTH_BOUNDARY.network_access_allowed = True  # type: ignore[misc]


def test_d2_policy_rejects_labels_signals_and_invalid_window() -> None:
    with pytest.raises(ValueError, match="metric-only"):
        _policy(threshold_or_crossover_allowed=True)
    with pytest.raises(ValueError, match="window"):
        _policy(window=1)


def test_d3_adx_metrics_are_exact_recursive_and_deterministic() -> None:
    evidence = _build()
    assert evidence.positive_di == Decimal("10.0000")
    assert evidence.negative_di == Decimal("26.6667")
    assert evidence.dx == Decimal("45.4545")
    assert evidence.adx == Decimal("51.2987")
    assert evidence.evidence_hash == _build().evidence_hash


def test_d3_flat_history_has_explicit_zero_metrics() -> None:
    evidence = _build(((10, 10, 10, 10),) * 4)
    assert evidence.positive_di == Decimal("0.0000")
    assert evidence.negative_di == Decimal("0.0000")
    assert evidence.dx == Decimal("0.0000")
    assert evidence.adx == Decimal("0.0000")


def test_d4_insufficient_history_is_blocked() -> None:
    evidence = _build(((9, 10, 8, 9), (10, 12, 9, 11), (11, 13, 10, 12)))
    assert evidence.required_samples == 4
    assert evidence.reason_codes == ("INSUFFICIENT_HISTORY_BLOCKED",)


def test_d4_future_availability_is_blocked() -> None:
    series = _series(((9, 10, 8, 9), (10, 12, 9, 11), (11, 13, 10, 12), (10, 12, 8, 9)))
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
    missing_factor = _build(policy=_policy(factor_definition_ref="missing@v1"))
    wrong_series = _build(policy=_policy(instrument_id="registered-btc"))
    assert wrong_registry.reason_codes == ("REGISTRY_IDENTITY_MISMATCH",)
    assert missing_factor.reason_codes == ("FACTOR_DEFINITION_NOT_REGISTERED",)
    assert wrong_series.reason_codes == ("SERIES_IDENTITY_MISMATCH",)


def test_d5_ledger_rejects_duplicate_and_invalid_capacity() -> None:
    evidence = _build()
    ledger = DirectionalStrengthLedger().append(evidence)
    with pytest.raises(ValueError, match="duplicate"):
        ledger.append(evidence)
    with pytest.raises(ValueError, match="capacity"):
        DirectionalStrengthLedger(capacity=0)


def test_d6_read_model_and_acceptance_are_non_activating() -> None:
    evidence = _build()
    model = build_read_model(DirectionalStrengthLedger().append(evidence))
    acceptance = build_operator_acceptance(evidence)
    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["trend_label"] is False
    assert model.payload["direction_claim"] is False
    assert model.payload["order_or_execution"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    assert acceptance.signal_or_recommendation_allowed is False
