from dataclasses import replace

import pytest

from apps.shadow_observation_runtime_app_1 import (
    ContradictionRecord,
    LoadedObservationDataset,
    ObservationPolicy,
    ObservationRecord,
    ObservationWindow,
    RegisteredObservationArtifact,
    RiskFlag,
    ShadowObservationRequest,
    build_operator_review_packet,
    build_shadow_observation_result_packet,
    evaluate_shadow_observation,
)


def _request(
    maximum_regression=0.1,
):
    return ShadowObservationRequest(
        run_id="shadow-run-d4",
        correlation_id="corr-d4",
        operator_trigger_id="operator-d4",
        artifact=RegisteredObservationArtifact(
            artifact_id="artifact-d4",
            artifact_version="v1",
            correlation_id="corr-d4",
            content_sha256="a" * 64,
            relative_path="shadow.json",
        ),
        window=ObservationWindow(
            window_id="window-d4",
            decision_time_utc="2026-01-01T00:00:00Z",
            observation_start_utc="2026-01-02T00:00:00Z",
            observation_cutoff_utc="2026-01-10T00:00:00Z",
        ),
        policy=ObservationPolicy(
            policy_id="policy-d4",
            minimum_observed_outcomes=2,
            minimum_candidate_coverage=1.0,
            maximum_candidate_mae_regression=maximum_regression,
            required_segments=("equity",),
            minimum_segment_outcomes=1,
            maximum_segment_mae_regression=maximum_regression,
        ),
    )


def _record(
    record_id,
    baseline_score,
    candidate_score,
    actual_outcome,
):
    return ObservationRecord(
        record_id=record_id,
        correlation_id="corr-d4",
        segment="equity",
        decision_time_utc="2026-01-01T00:00:00Z",
        observation_time_utc="2026-01-03T00:00:00Z",
        baseline_score=baseline_score,
        candidate_score=candidate_score,
        actual_outcome=actual_outcome,
    )


def _dataset(
    request,
    records,
):
    return LoadedObservationDataset(
        request=request,
        records=tuple(records),
        source_path="shadow.json",
        source_sha256="a" * 64,
    )


def _ready_components():
    request = _request()
    dataset = _dataset(
        request,
        (
            _record("r1", 0.6, 0.8, 1.0),
            _record("r2", 0.4, 0.2, 0.0),
        ),
    )
    observation = evaluate_shadow_observation(dataset)
    return request, dataset, observation


def test_d4_risk_flag_normalizes_severity():
    flag = RiskFlag(
        code="risk-1",
        severity="high",
        message="Review required",
        blocking=True,
    )

    assert flag.severity == "HIGH"
    assert flag.blocking is True


def test_d4_builds_ready_result_and_review_packet():
    request, dataset, observation = _ready_components()

    result = build_shadow_observation_result_packet(
        request=request,
        dataset=dataset,
        observation=observation,
    )
    review = build_operator_review_packet(result)

    assert result.status == "READY_FOR_OPERATOR_REVIEW"
    assert result.operator_review_required is True
    assert result.automatic_approval_allowed is False
    assert result.automatic_promotion_allowed is False
    assert review.required_action == "OPERATOR_DECISION_REQUIRED"
    assert "CONTINUE_PASSIVE_OBSERVATION_ONLY" in (
        review.permitted_operator_actions
    )


def test_d4_degraded_observation_remains_review_gated():
    request = _request(maximum_regression=0.01)
    dataset = _dataset(
        request,
        (
            _record("r1", 1.0, 0.0, 1.0),
            _record("r2", 0.0, 1.0, 0.0),
        ),
    )
    observation = evaluate_shadow_observation(dataset)

    result = build_shadow_observation_result_packet(
        request=request,
        dataset=dataset,
        observation=observation,
    )

    assert result.status == "DEGRADED"
    assert result.recommendation == (
        "OPERATOR_REVIEW_DEGRADED_EVIDENCE"
    )


def test_d4_blocking_risk_forces_block():
    request, dataset, observation = _ready_components()

    result = build_shadow_observation_result_packet(
        request=request,
        dataset=dataset,
        observation=observation,
        risk_flags=(
            RiskFlag(
                code="manual-block",
                severity="HIGH",
                message="Blocking evidence",
                blocking=True,
            ),
        ),
    )

    assert result.status == "BLOCKED"
    assert result.recommendation == "DO_NOT_ADVANCE"


def test_d4_high_unresolved_contradiction_forces_block():
    request, dataset, observation = _ready_components()

    result = build_shadow_observation_result_packet(
        request=request,
        dataset=dataset,
        observation=observation,
        contradictions=(
            ContradictionRecord(
                contradiction_id="contradiction-1",
                correlation_id="corr-d4",
                category="regime_conflict",
                statement_a="baseline stable",
                statement_b="candidate unstable",
                severity="HIGH",
                unresolved=True,
                evidence_ids=("evidence-1",),
            ),
        ),
    )

    assert result.status == "BLOCKED"
    assert len(result.contradictions) == 1


def test_d4_review_packet_prohibits_governance_actions():
    request, dataset, observation = _ready_components()
    result = build_shadow_observation_result_packet(
        request=request,
        dataset=dataset,
        observation=observation,
    )
    review = build_operator_review_packet(result)

    with pytest.raises(
        ValueError,
        match="prohibited review action",
    ):
        replace(
            review,
            promotion_action_available=True,
        )
