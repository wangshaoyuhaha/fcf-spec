from dataclasses import FrozenInstanceError, replace
from decimal import Decimal
from types import MappingProxyType

import pytest

from apps.v2_r4_local_anomaly_radar_foundation_app_1 import AnomalyEvidence
from apps.v2_r5_local_cognitive_shield_foundation_app_1 import CognitiveShieldEvidence
from apps.v2_r6_local_paper_scenario_research_foundation_app_1 import (
    V2_R6_LOCAL_PAPER_SCENARIO_BOUNDARY,
    PaperScenarioLedger,
    PaperScenarioPolicy,
    RegisteredObservationPoint,
    V2R6LocalPaperScenarioBoundary,
    build_operator_acceptance,
    build_read_model,
    evaluate_paper_scenario,
)


def _anomaly(*, state: str = "CONFIRMED") -> AnomalyEvidence:
    return AnomalyEvidence(
        rule_id="registered-anomaly-rule",
        rule_version="v1",
        context_id="registered-local-context",
        stream_id="registered-stream",
        event_id="registered-event",
        state=state,
        value=Decimal("100"),
        z_score=Decimal("3"),
        velocity_per_second=Decimal("0.1"),
        persistence_count=2,
        negative_evidence=(),
        reason_codes=("REGISTERED_TEST",),
        observed_at_utc="2026-01-01T00:00:00Z",
        expires_at_utc="2026-01-01T00:10:00Z",
        baseline_replay_hash="b" * 64,
        evidence_hash="a" * 64,
    )


def _shield(*, state: str = "SUPPORTED_REVIEW") -> CognitiveShieldEvidence:
    return CognitiveShieldEvidence(
        task_id="registered-cognitive-task",
        anomaly_evidence_hash="a" * 64,
        anomaly_state="CONFIRMED",
        shield_state=state,
        advisory_stance="SUPPORT",
        advisory_confidence=Decimal("0.80"),
        uncertainty_state="NONE",
        reason_codes=("REGISTERED_TEST",),
        deterministic_evidence_preserved=True,
        explanation_used=True,
        operator_review_required=True,
        evaluated_at_utc="2026-01-01T00:00:00Z",
        shield_evidence_hash="d" * 64,
    )


def _policy(*, direction: str = "UP") -> PaperScenarioPolicy:
    return PaperScenarioPolicy(
        scenario_id="registered-paper-scenario",
        scenario_version="v1",
        research_direction=direction,
        horizon_seconds=120,
        cost_assumption_bps=Decimal("10"),
        minimum_points=2,
    )


def _point(sequence: int, minute: int, price: str, *, available_minute: int | None = None) -> RegisteredObservationPoint:
    available = minute if available_minute is None else available_minute
    return RegisteredObservationPoint(
        point_id=f"registered-point-{sequence}",
        sequence=sequence,
        observed_at_utc=f"2026-01-01T00:{minute:02d}:00Z",
        available_at_utc=f"2026-01-01T00:{available:02d}:00Z",
        price=Decimal(price),
        source_artifact_hash=f"{sequence}" * 64,
    )


def _evaluate(*, direction: str = "UP", end_price: str = "105", shield_state: str = "SUPPORTED_REVIEW"):
    return evaluate_paper_scenario(
        _anomaly(),
        _shield(state=shield_state),
        _policy(direction=direction),
        (_point(1, 0, "100"), _point(2, 1, end_price)),
        as_of_utc="2026-01-01T00:01:01Z",
    )


def test_d1_boundary_is_closed_and_immutable() -> None:
    boundary = V2_R6_LOCAL_PAPER_SCENARIO_BOUNDARY

    assert boundary.local_only is True
    assert boundary.virtual_account_allowed is False
    assert boundary.paper_order_allowed is False
    assert boundary.leverage_allowed is False
    assert boundary.real_execution_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R6LocalPaperScenarioBoundary(paper_order_allowed=True)
    with pytest.raises(FrozenInstanceError):
        boundary.leverage_allowed = True  # type: ignore[misc]


def test_d2_policy_rejects_order_leverage_and_market_calibration_claims() -> None:
    with pytest.raises(ValueError, match="research-only scope"):
        replace(_policy(), paper_order_allowed=True)
    with pytest.raises(ValueError, match="uncalibrated"):
        replace(_policy(), market_calibrated=True)


def test_d2_observation_contract_rejects_nonpositive_price() -> None:
    with pytest.raises(ValueError, match="price must be positive"):
        _point(1, 0, "0")


def test_d3_up_scenario_metrics_are_deterministic() -> None:
    evidence = _evaluate()
    repeated = _evaluate()

    assert evidence.state == "EVALUATED"
    assert evidence.outcome == "POSITIVE_OBSERVATION"
    assert evidence.raw_path_return == Decimal("0.05")
    assert evidence.aligned_research_return == Decimal("0.05")
    assert evidence.cost_adjusted_return == Decimal("0.049")
    assert evidence.maximum_favorable_movement == Decimal("0.05")
    assert evidence.maximum_adverse_movement == Decimal("0")
    assert evidence.evidence_hash == repeated.evidence_hash


def test_d3_down_scenario_aligns_research_direction() -> None:
    evidence = _evaluate(direction="DOWN", end_price="95")

    assert evidence.raw_path_return == Decimal("-0.05")
    assert evidence.aligned_research_return == Decimal("0.05")
    assert evidence.cost_adjusted_return == Decimal("0.049")


def test_d4_degraded_anomaly_and_unusable_shield_block_metrics() -> None:
    degraded = evaluate_paper_scenario(
        _anomaly(state="DEGRADED"),
        _shield(),
        _policy(),
        (_point(1, 0, "100"), _point(2, 1, "105")),
        as_of_utc="2026-01-01T00:01:01Z",
    )
    blocked = _evaluate(shield_state="BLOCKED")

    assert degraded.state == "BLOCKED"
    assert degraded.raw_path_return is None
    assert blocked.state == "BLOCKED"
    assert blocked.outcome == "NOT_EVALUATED"


def test_d4_future_availability_is_rejected_as_leakage() -> None:
    with pytest.raises(ValueError, match="future evidence"):
        evaluate_paper_scenario(
            _anomaly(),
            _shield(),
            _policy(),
            (_point(1, 0, "100"), _point(2, 1, "105", available_minute=2)),
            as_of_utc="2026-01-01T00:01:01Z",
        )


def test_d4_sequence_and_horizon_fail_closed() -> None:
    with pytest.raises(ValueError, match="contiguous"):
        evaluate_paper_scenario(
            _anomaly(), _shield(), _policy(),
            (_point(1, 0, "100"), _point(3, 1, "105")),
            as_of_utc="2026-01-01T00:01:01Z",
        )
    with pytest.raises(ValueError, match="horizon"):
        evaluate_paper_scenario(
            _anomaly(), _shield(), _policy(),
            (_point(1, 0, "100"), _point(2, 3, "105")),
            as_of_utc="2026-01-01T00:03:01Z",
        )


def test_d5_ledger_rejects_duplicate_scenario_evidence() -> None:
    evidence = _evaluate()
    ledger = PaperScenarioLedger().append(evidence)

    with pytest.raises(ValueError, match="duplicate Paper scenario"):
        ledger.append(evidence)


def test_d6_read_model_and_acceptance_are_non_trading() -> None:
    evidence = _evaluate()
    model = build_read_model(PaperScenarioLedger().append(evidence))
    acceptance = build_operator_acceptance(evidence)

    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["virtual_account"] is False
    assert model.payload["paper_order"] is False
    assert model.payload["leverage"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    assert acceptance.order_created is False
    with pytest.raises(TypeError):
        model.payload["paper_order"] = True  # type: ignore[index]
