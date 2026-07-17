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
from apps.v2_r13_local_momentum_indicator_foundation_app_1 import (
    V2_R13_MOMENTUM_INDICATOR_BOUNDARY,
    MomentumIndicatorLedger,
    MomentumIndicatorPolicy,
    V2R13MomentumIndicatorBoundary,
    build_momentum_indicator,
    build_operator_acceptance,
    build_read_model,
)


def _registry():
    definition = FactorDefinition(
        "registered-momentum",
        "v1",
        "TECHNICAL",
        "RESEARCH",
        "DETERMINISTIC_CODE",
        "b" * 64,
        "percent",
        ("equity",),
        ("close",),
        minimum_lookback=2,
        maximum_lookback=200,
    )
    return build_factor_registry(
        (definition,),
        FactorRegistryPolicy("registered-factor-registry", "v1"),
        as_of_utc="2026-01-06T01:00:00Z",
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
    return RegisteredPriceSeries("registered-momentum-series", points)


def _policy(**changes: object) -> MomentumIndicatorPolicy:
    data: dict[str, object] = {
        "indicator_id": "registered-rsi",
        "indicator_version": "v1",
        "indicator_type": "RSI",
        "factor_definition_ref": "registered-momentum@v1",
        "registry_id": "registered-factor-registry",
        "registry_version": "v1",
        "instrument_id": "registered-equity",
        "interval_id": "registered-daily",
        "window": 4,
        "decimal_places": 4,
    }
    data.update(changes)
    return MomentumIndicatorPolicy(**data)  # type: ignore[arg-type]


def _build(
    values: tuple[object, ...] = (10, 11, 10, 12, 11),
    **changes: object,
):
    return build_momentum_indicator(
        changes.get("series", _series(values)),  # type: ignore[arg-type]
        changes.get("registry", _registry()),  # type: ignore[arg-type]
        changes.get("policy", _policy()),  # type: ignore[arg-type]
        as_of_utc=str(changes.get("as_of_utc", "2026-01-06T01:00:00Z")),
    )


def test_d1_boundary_is_closed_and_immutable() -> None:
    assert V2_R13_MOMENTUM_INDICATOR_BOUNDARY.prediction_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R13MomentumIndicatorBoundary(score_rank_or_signal_allowed=True)
    with pytest.raises(FrozenInstanceError):
        V2_R13_MOMENTUM_INDICATOR_BOUNDARY.network_access_allowed = True  # type: ignore[misc]


def test_d2_policy_rejects_signal_and_invalid_window() -> None:
    with pytest.raises(ValueError, match="calculation-only"):
        _policy(score_rank_or_signal_allowed=True)
    with pytest.raises(ValueError, match="window"):
        _policy(window=1)


def test_d3_mixed_rsi_is_exact_and_deterministic() -> None:
    evidence = _build()
    assert evidence.state == "MOMENTUM_READY"
    assert evidence.rsi == Decimal("60.0000")
    assert evidence.evidence_hash == _build().evidence_hash


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ((1, 2, 3, 4, 5), Decimal("100.0000")),
        ((5, 4, 3, 2, 1), Decimal("0.0000")),
        ((3, 3, 3, 3, 3), Decimal("50.0000")),
    ],
)
def test_d3_rsi_edge_states_are_explicit(
    values: tuple[object, ...], expected: Decimal
) -> None:
    assert _build(values).rsi == expected


def test_d3_rate_of_change_is_exact() -> None:
    evidence = _build(policy=_policy(indicator_type="RATE_OF_CHANGE"))
    assert evidence.rate_of_change == Decimal("10.0000")
    assert evidence.rsi is None


def test_d4_insufficient_window_is_blocked() -> None:
    evidence = _build(series=_series((1, 2, 3, 4)))
    assert evidence.reason_codes == ("INSUFFICIENT_WINDOW_BLOCKED",)


def test_d4_future_availability_is_blocked() -> None:
    series = _series((1, 2, 3, 4, 5))
    last = series.points[-1]
    future = RegisteredPricePoint(
        point_id=last.point_id,
        instrument_id=last.instrument_id,
        interval_id=last.interval_id,
        observed_at_utc=last.observed_at_utc,
        available_at_utc="2026-01-07T00:00:00Z",
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
    ledger = MomentumIndicatorLedger().append(evidence)
    with pytest.raises(ValueError, match="duplicate"):
        ledger.append(evidence)
    with pytest.raises(ValueError, match="capacity"):
        MomentumIndicatorLedger(capacity=0)


def test_d6_read_model_and_acceptance_are_non_activating() -> None:
    evidence = _build()
    model = build_read_model(MomentumIndicatorLedger().append(evidence))
    acceptance = build_operator_acceptance(evidence)
    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["score_rank_or_signal"] is False
    assert model.payload["order_or_execution"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    assert acceptance.signal_or_recommendation_allowed is False
