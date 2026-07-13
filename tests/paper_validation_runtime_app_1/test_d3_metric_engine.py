from apps.paper_validation_runtime_app_1.domain import (
    ComparisonPolicy,
    ValidationSample,
)
from apps.paper_validation_runtime_app_1.metric_engine import evaluate_candidate


def _sample(
    sample_id: str,
    segment: str,
    baseline_score: float,
    candidate_score: float | None,
    actual_outcome: float,
    *,
    eligible: bool = True,
    exclusion_reason: str = "",
) -> ValidationSample:
    return ValidationSample(
        sample_id=sample_id,
        segment=segment,
        decision_time_utc="2026-01-20T00:00:00Z",
        outcome_time_utc="2026-02-10T00:00:00Z",
        baseline_score=baseline_score,
        candidate_score=candidate_score,
        actual_outcome=actual_outcome,
        eligible=eligible,
        exclusion_reason=exclusion_reason,
    )


def _policy(**overrides: object) -> ComparisonPolicy:
    values = {
        "policy_id": "policy-001",
        "minimum_eligible_samples": 2,
        "minimum_candidate_coverage": 1.0,
        "maximum_mae_regression": 0.0,
        "minimum_accuracy_delta": 0.0,
        "required_segments": ("large_cap", "small_cap"),
        "minimum_segment_samples": 1,
        "maximum_segment_mae_regression": 0.0,
    }
    values.update(overrides)
    return ComparisonPolicy(**values)


def _good_samples() -> tuple[ValidationSample, ...]:
    return (
        _sample("s1", "large_cap", 0.55, 0.90, 1.0),
        _sample("s2", "small_cap", 0.45, 0.10, 0.0),
    )


def test_improving_candidate_is_ready_for_operator_review_only() -> None:
    packet = evaluate_candidate(
        run_id="run-001",
        correlation_id="corr-001",
        samples=_good_samples(),
        policy=_policy(),
    )

    assert packet.status == "READY_FOR_OPERATOR_REVIEW"
    assert packet.recommendation == "CANDIDATE_MAY_PROCEED_TO_OPERATOR_REVIEW"
    assert packet.blocking_reasons == ()
    assert packet.operator_review_required is True
    assert packet.automatic_approval_allowed is False
    assert packet.automatic_promotion_allowed is False
    assert packet.automatic_baseline_replacement_allowed is False
    assert packet.overall_metrics.mae_delta < 0
    assert packet.overall_metrics.accuracy_delta >= 0


def test_insufficient_samples_block_candidate() -> None:
    packet = evaluate_candidate(
        run_id="run-002",
        correlation_id="corr-002",
        samples=(_good_samples()[0],),
        policy=_policy(minimum_eligible_samples=3),
    )

    assert packet.status == "BLOCKED"
    assert "INSUFFICIENT_ELIGIBLE_SAMPLES" in packet.blocking_reasons


def test_missing_required_segment_blocks_candidate() -> None:
    packet = evaluate_candidate(
        run_id="run-003",
        correlation_id="corr-003",
        samples=(
            _sample("s1", "large_cap", 0.55, 0.90, 1.0),
            _sample("s2", "large_cap", 0.45, 0.10, 0.0),
        ),
        policy=_policy(),
    )

    assert packet.status == "BLOCKED"
    assert "MISSING_REQUIRED_SEGMENT:small_cap" in packet.blocking_reasons


def test_candidate_abstention_can_block_coverage() -> None:
    samples = (
        _sample("s1", "large_cap", 0.55, 0.90, 1.0),
        _sample("s2", "small_cap", 0.45, None, 0.0),
    )

    packet = evaluate_candidate(
        run_id="run-004",
        correlation_id="corr-004",
        samples=samples,
        policy=_policy(minimum_candidate_coverage=0.75),
    )

    assert packet.status == "BLOCKED"
    assert "INSUFFICIENT_CANDIDATE_COVERAGE" in packet.blocking_reasons
    assert "CANDIDATE_ABSTENTIONS_PRESENT" in packet.review_reasons
    assert packet.overall_metrics.candidate_coverage == 0.5


def test_mae_regression_blocks_candidate() -> None:
    samples = (
        _sample("s1", "large_cap", 0.90, 0.55, 1.0),
        _sample("s2", "small_cap", 0.10, 0.45, 0.0),
    )

    packet = evaluate_candidate(
        run_id="run-005",
        correlation_id="corr-005",
        samples=samples,
        policy=_policy(),
    )

    assert packet.status == "BLOCKED"
    assert "OVERALL_MAE_REGRESSION" in packet.blocking_reasons
    assert "SEGMENT_MAE_REGRESSION:large_cap" in packet.blocking_reasons
    assert "SEGMENT_MAE_REGRESSION:small_cap" in packet.blocking_reasons


def test_excluded_samples_are_preserved_for_review() -> None:
    samples = _good_samples() + (
        _sample(
            "s3",
            "large_cap",
            0.50,
            0.50,
            1.0,
            eligible=False,
            exclusion_reason="MISSING_REQUIRED_FIELD_AT_DECISION_TIME",
        ),
    )

    packet = evaluate_candidate(
        run_id="run-006",
        correlation_id="corr-006",
        samples=samples,
        policy=_policy(),
    )

    assert packet.status == "READY_FOR_OPERATOR_REVIEW"
    assert packet.overall_metrics.total_samples == 3
    assert packet.overall_metrics.eligible_samples == 2
    assert packet.overall_metrics.excluded_samples == 1
    assert "EXCLUDED_SAMPLES_PRESENT" in packet.review_reasons


def test_metric_output_is_deterministic() -> None:
    first = evaluate_candidate(
        run_id="run-007",
        correlation_id="corr-007",
        samples=_good_samples(),
        policy=_policy(),
    )
    second = evaluate_candidate(
        run_id="run-007",
        correlation_id="corr-007",
        samples=_good_samples(),
        policy=_policy(),
    )

    assert first.as_dict() == second.as_dict()
