from __future__ import annotations

from dataclasses import replace

import pytest

from apps.paper_validation_runtime_app_1.domain import (
    ComparisonPolicy,
    EvaluationWindow,
    RegisteredArtifact,
    ValidationRunRequest,
)
from apps.paper_validation_runtime_app_1.input_loader import LoadedValidationDataset
from apps.paper_validation_runtime_app_1.metric_engine import (
    ComparisonPacket,
    MetricSummary,
)
from apps.paper_validation_runtime_app_1.packet_builder import (
    ContradictionRecord,
    RiskFlag,
    build_operator_review_packet,
    build_validation_result_packet,
    derive_comparison_risk_flags,
)


def _request() -> ValidationRunRequest:
    return ValidationRunRequest(
        run_id="run-001",
        correlation_id="corr-001",
        artifact_id="artifact-001",
        artifact_version="v1",
        window=EvaluationWindow(
            window_id="window-001",
            start_time_utc="2026-01-01T00:00:00Z",
            decision_cutoff_utc="2026-01-02T00:00:00Z",
            observation_cutoff_utc="2026-01-03T00:00:00Z",
            end_time_utc="2026-01-03T00:00:00Z",
        ),
        policy=ComparisonPolicy(
            policy_id="policy-001",
            minimum_eligible_samples=1,
            minimum_candidate_coverage=0.0,
            maximum_mae_regression=1.0,
            minimum_accuracy_delta=-1.0,
        ),
        operator_trigger_id="operator-trigger-001",
    )


def _dataset(request: ValidationRunRequest) -> LoadedValidationDataset:
    return LoadedValidationDataset(
        artifact=RegisteredArtifact(
            artifact_id=request.artifact_id,
            artifact_version=request.artifact_version,
            correlation_id=request.correlation_id,
            content_sha256="1" * 64,
            relative_path="registered.json",
        ),
        window=request.window,
        samples=(object(),),
        source_path="registered.json",
        source_sha256="1" * 64,
    )


def _comparison(
    request: ValidationRunRequest,
    *,
    status: str = "READY_FOR_OPERATOR_REVIEW",
    blocking: tuple[str, ...] = (),
    review: tuple[str, ...] = ("OPERATOR_DECISION_REQUIRED",),
) -> ComparisonPacket:
    metrics = MetricSummary(
        total_samples=2,
        eligible_samples=2,
        excluded_samples=0,
        candidate_scored_samples=2,
        candidate_abstentions=0,
        candidate_coverage=1.0,
        baseline_mae=0.2,
        candidate_mae=0.1,
        mae_delta=-0.1,
        baseline_accuracy=0.5,
        candidate_accuracy=1.0,
        accuracy_delta=0.5,
    )
    return ComparisonPacket(
        run_id=request.run_id,
        correlation_id=request.correlation_id,
        policy_id=request.policy.policy_id,
        status=status,
        recommendation=(
            "DO_NOT_ADVANCE"
            if status == "BLOCKED"
            else "CANDIDATE_MAY_PROCEED_TO_OPERATOR_REVIEW"
        ),
        overall_metrics=metrics,
        segment_metrics={},
        blocking_reasons=blocking,
        review_reasons=review,
    )


def test_derive_comparison_risk_flags_preserves_blocking_and_review() -> None:
    request = _request()
    comparison = _comparison(
        request,
        status="BLOCKED",
        blocking=("INSUFFICIENT_ELIGIBLE_SAMPLES",),
        review=("EXCLUDED_SAMPLES_PRESENT",),
    )

    flags = derive_comparison_risk_flags(comparison)

    assert [flag.code for flag in flags] == [
        "INSUFFICIENT_ELIGIBLE_SAMPLES",
        "EXCLUDED_SAMPLES_PRESENT",
    ]
    assert flags[0].blocking is True
    assert flags[0].severity == "HIGH"
    assert flags[1].blocking is False
    assert flags[1].severity == "MEDIUM"


def test_result_packet_preserves_risk_and_contradiction_evidence() -> None:
    request = _request()
    dataset = _dataset(request)
    comparison = _comparison(request)
    custom_flag = RiskFlag(
        code="MANUAL_EVIDENCE_GAP",
        severity="MEDIUM",
        message="Operator supplied evidence gap",
        blocking=False,
        source="operator_review",
    )
    contradiction = ContradictionRecord(
        contradiction_id="contradiction-001",
        correlation_id=request.correlation_id,
        category="metric_conflict",
        statement_a="candidate improves MAE",
        statement_b="candidate regresses required segment",
        severity="MEDIUM",
        evidence_ids=("metric:overall", "metric:segment"),
    )

    packet = build_validation_result_packet(
        request=request,
        dataset=dataset,
        comparison=comparison,
        risk_flags=(custom_flag,),
        contradictions=(contradiction,),
    )

    assert packet.status == "READY_FOR_OPERATOR_REVIEW"
    assert custom_flag in packet.risk_flags
    assert packet.contradictions == (contradiction,)
    assert packet.operator_review_required is True
    assert packet.automatic_approval_allowed is False
    assert packet.automatic_promotion_allowed is False
    assert packet.automatic_baseline_replacement_allowed is False


def test_blocking_risk_flag_forces_blocked_status() -> None:
    request = _request()
    packet = build_validation_result_packet(
        request=request,
        dataset=_dataset(request),
        comparison=_comparison(request),
        risk_flags=(
            RiskFlag(
                code="DATA_INTEGRITY_BLOCK",
                severity="CRITICAL",
                message="Registered evidence cannot be trusted",
                blocking=True,
            ),
        ),
    )

    assert packet.status == "BLOCKED"
    assert packet.recommendation == "DO_NOT_ADVANCE"


def test_high_unresolved_contradiction_forces_blocked_status() -> None:
    request = _request()
    contradiction = ContradictionRecord(
        contradiction_id="contradiction-002",
        correlation_id=request.correlation_id,
        category="authority_conflict",
        statement_a="registered artifact is immutable",
        statement_b="observed artifact hash differs",
        severity="HIGH",
        unresolved=True,
    )

    packet = build_validation_result_packet(
        request=request,
        dataset=_dataset(request),
        comparison=_comparison(request),
        contradictions=(contradiction,),
    )

    assert packet.status == "BLOCKED"
    assert packet.contradictions == (contradiction,)


def test_contradiction_correlation_mismatch_is_rejected() -> None:
    request = _request()
    contradiction = ContradictionRecord(
        contradiction_id="contradiction-003",
        correlation_id="corr-other",
        category="identity_conflict",
        statement_a="corr-001",
        statement_b="corr-other",
        severity="HIGH",
    )

    with pytest.raises(ValueError, match="contradiction correlation_id mismatch"):
        build_validation_result_packet(
            request=request,
            dataset=_dataset(request),
            comparison=_comparison(request),
            contradictions=(contradiction,),
        )


def test_operator_review_packet_never_exposes_promotion_or_execution() -> None:
    request = _request()
    result = build_validation_result_packet(
        request=request,
        dataset=_dataset(request),
        comparison=_comparison(request),
    )

    review = build_operator_review_packet(result)

    assert review.operator_review_required is True
    assert review.automatic_decision_allowed is False
    assert review.promotion_action_available is False
    assert review.baseline_replacement_action_available is False
    assert review.learning_activation_action_available is False
    assert review.real_execution_action_available is False
    assert "ACCEPT_FOR_FURTHER_PAPER_REVIEW_ONLY" in review.permitted_operator_actions
    assert all("PROMOTE" not in action for action in review.permitted_operator_actions)


def test_result_packet_identity_mismatch_is_rejected() -> None:
    request = _request()
    dataset = _dataset(request)
    mismatched = replace(
        dataset,
        artifact=replace(dataset.artifact, artifact_id="artifact-other"),
    )

    with pytest.raises(ValueError, match="dataset artifact_id mismatch"):
        build_validation_result_packet(
            request=request,
            dataset=mismatched,
            comparison=_comparison(request),
        )
