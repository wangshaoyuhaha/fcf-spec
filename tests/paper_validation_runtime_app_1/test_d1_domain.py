import pytest

from apps.paper_validation_runtime_app_1.domain import (
    PAPER_VALIDATION_RUNTIME_BOUNDARY,
    ComparisonPolicy,
    EvaluationWindow,
    RuntimeBoundary,
    ValidationRunRequest,
    ValidationSample,
)


def _window() -> EvaluationWindow:
    return EvaluationWindow(
        window_id="window-001",
        start_time_utc="2026-01-01T00:00:00Z",
        decision_cutoff_utc="2026-01-31T00:00:00Z",
        observation_cutoff_utc="2026-02-28T00:00:00Z",
        end_time_utc="2026-02-28T00:00:00Z",
    )


def _policy() -> ComparisonPolicy:
    return ComparisonPolicy(
        policy_id="policy-001",
        minimum_eligible_samples=2,
        minimum_candidate_coverage=0.8,
        maximum_mae_regression=0.0,
        minimum_accuracy_delta=0.0,
        required_segments=("large_cap",),
        minimum_segment_samples=1,
        maximum_segment_mae_regression=0.0,
    )


def test_boundary_is_local_paper_only_and_fail_closed() -> None:
    boundary = PAPER_VALIDATION_RUNTIME_BOUNDARY

    assert boundary.local_only is True
    assert boundary.read_only_inputs is True
    assert boundary.operator_trigger_required is True
    assert boundary.operator_review_required is True
    assert boundary.network_access_allowed is False
    assert boundary.real_order_allowed is False
    assert boundary.real_execution_allowed is False
    assert boundary.automatic_approval_allowed is False
    assert boundary.automatic_promotion_allowed is False
    assert boundary.shadow_runtime_allowed is False


def test_boundary_rejects_prohibited_capability() -> None:
    with pytest.raises(ValueError, match="prohibited runtime capability"):
        RuntimeBoundary(network_access_allowed=True)


def test_evaluation_window_requires_strict_cutoff_order() -> None:
    with pytest.raises(ValueError, match="start < decision < observation <= end"):
        EvaluationWindow(
            window_id="bad-window",
            start_time_utc="2026-01-01T00:00:00Z",
            decision_cutoff_utc="2026-02-01T00:00:00Z",
            observation_cutoff_utc="2026-01-31T00:00:00Z",
            end_time_utc="2026-02-28T00:00:00Z",
        )


def test_validation_sample_rejects_outcome_before_decision() -> None:
    with pytest.raises(ValueError, match="after decision_time_utc"):
        ValidationSample(
            sample_id="sample-001",
            segment="large_cap",
            decision_time_utc="2026-01-10T00:00:00Z",
            outcome_time_utc="2026-01-09T00:00:00Z",
            baseline_score=0.6,
            candidate_score=0.7,
            actual_outcome=1.0,
        )


def test_run_request_requires_explicit_operator_trigger() -> None:
    with pytest.raises(ValueError, match="operator_trigger_id is required"):
        ValidationRunRequest(
            run_id="run-001",
            correlation_id="corr-001",
            artifact_id="artifact-001",
            artifact_version="v1",
            window=_window(),
            policy=_policy(),
            operator_trigger_id="",
        )
