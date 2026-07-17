from dataclasses import FrozenInstanceError, replace
from decimal import Decimal
from types import MappingProxyType

import pytest

from apps.v2_r10_local_turnover_definition_research_foundation_app_1 import (
    V2_R10_LOCAL_TURNOVER_BOUNDARY,
    RegisteredTurnoverObservation,
    TurnoverLedger,
    TurnoverPolicy,
    V2R10LocalTurnoverBoundary,
    build_operator_acceptance,
    build_read_model,
    build_turnover,
)


def _policy(**changes: object) -> TurnoverPolicy:
    data: dict[str, object] = dict(definition_id="registered-turnover", definition_version="v1", instrument_id="registered-equity", phase="CONTINUOUS_SESSION", interval_id="registered-continuous-session", slot_index=5, denominator_type="FREE_FLOAT_SHARES", output_unit="PERCENT", decimal_places=4)
    data.update(changes)
    return TurnoverPolicy(**data)  # type: ignore[arg-type]


def _observation(**changes: object) -> RegisteredTurnoverObservation:
    data: dict[str, object] = dict(observation_id="registered-turnover-observation", session_evidence_hash="a" * 64, instrument_id="registered-equity", phase="CONTINUOUS_SESSION", interval_id="registered-continuous-session", slot_index=5, observed_at_utc="2026-01-05T01:05:00Z", volume_available_at_utc="2026-01-05T01:05:01Z", share_base_effective_at_utc="2026-01-01T00:00:00Z", share_base_available_at_utc="2026-01-02T00:00:00Z", traded_volume=Decimal("250"), share_base=Decimal("10000"), denominator_type="FREE_FLOAT_SHARES", volume_source_artifact_hash="b" * 64, share_base_source_artifact_hash="c" * 64)
    data.update(changes)
    return RegisteredTurnoverObservation(**data)  # type: ignore[arg-type]


def _build(**changes: object):
    return build_turnover(changes.get("observation", _observation()), changes.get("policy", _policy()), as_of_utc=str(changes.get("as_of_utc", "2026-01-05T01:06:00Z")))  # type: ignore[arg-type]


def test_d1_boundary_is_closed_and_immutable() -> None:
    assert V2_R10_LOCAL_TURNOVER_BOUNDARY.factor_activation_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R10LocalTurnoverBoundary(order_or_execution_allowed=True)
    with pytest.raises(FrozenInstanceError):
        V2_R10_LOCAL_TURNOVER_BOUNDARY.network_access_allowed = True  # type: ignore[misc]


def test_d2_policy_rejects_unknown_denominator_and_activation() -> None:
    with pytest.raises(ValueError, match="denominator"):
        _policy(denominator_type="MIXED")
    with pytest.raises(ValueError, match="research-only"):
        _policy(scoring_allowed=True)


def test_d2_observation_rejects_negative_and_future_effective_base() -> None:
    with pytest.raises(ValueError, match="bounded"):
        _observation(traded_volume=Decimal("-1"))
    with pytest.raises(ValueError, match="future-effective"):
        _observation(
            share_base_effective_at_utc="2026-01-06T00:00:00Z",
            share_base_available_at_utc="2026-01-06T00:00:01Z",
        )


def test_d3_percent_turnover_is_exact_and_deterministic() -> None:
    evidence = _build()
    assert evidence.state == "TURNOVER_READY"
    assert evidence.turnover == Decimal("2.5000")
    assert evidence.evidence_hash == _build().evidence_hash


def test_d3_fraction_unit_is_explicit() -> None:
    evidence = _build(policy=_policy(output_unit="FRACTION", decimal_places=6))
    assert evidence.output_unit == "FRACTION"
    assert evidence.turnover == Decimal("0.025000")


def test_d4_zero_share_base_is_blocked() -> None:
    evidence = _build(observation=_observation(share_base=Decimal("0")))
    assert evidence.reason_codes == ("ZERO_SHARE_BASE_BLOCKED",)
    assert evidence.turnover is None


def test_d4_future_availability_is_blocked() -> None:
    evidence = _build(observation=_observation(share_base_available_at_utc="2026-01-05T02:00:00Z"))
    assert evidence.reason_codes == ("FUTURE_SHARE_BASE_AVAILABILITY_BLOCKED",)


def test_d4_denominator_and_identity_mismatch_are_blocked() -> None:
    denominator = _build(observation=_observation(denominator_type="TOTAL_SHARES"))
    identity = _build(observation=_observation(instrument_id="different-equity"))
    assert denominator.reason_codes == ("DENOMINATOR_TYPE_MISMATCH",)
    assert identity.reason_codes == ("INSTRUMENT_MISMATCH",)


def test_d5_ledger_rejects_duplicate_evidence() -> None:
    evidence = _build()
    ledger = TurnoverLedger().append(evidence)
    with pytest.raises(ValueError, match="duplicate turnover"):
        ledger.append(evidence)
    with pytest.raises(ValueError, match="natural key"):
        ledger.append(replace(evidence, evidence_hash="d" * 64))
    with pytest.raises(ValueError, match="capacity"):
        TurnoverLedger(capacity=0)


def test_d6_read_model_and_acceptance_remain_non_activating() -> None:
    evidence = _build()
    model = build_read_model(TurnoverLedger().append(evidence))
    acceptance = build_operator_acceptance(evidence)
    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["factor_activated"] is False
    assert model.payload["order_or_execution"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
