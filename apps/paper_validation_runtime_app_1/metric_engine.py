from __future__ import annotations

from dataclasses import dataclass
from math import fsum
from typing import Iterable, Mapping, Sequence, Tuple

from .domain import ComparisonPolicy, ValidationSample


def _rounded(value: float) -> float:
    return round(float(value), 12)


@dataclass(frozen=True)
class MetricSummary:
    total_samples: int
    eligible_samples: int
    excluded_samples: int
    candidate_scored_samples: int
    candidate_abstentions: int
    candidate_coverage: float
    baseline_mae: float
    candidate_mae: float
    mae_delta: float
    baseline_accuracy: float
    candidate_accuracy: float
    accuracy_delta: float

    def as_dict(self) -> dict[str, object]:
        return {
            "total_samples": self.total_samples,
            "eligible_samples": self.eligible_samples,
            "excluded_samples": self.excluded_samples,
            "candidate_scored_samples": self.candidate_scored_samples,
            "candidate_abstentions": self.candidate_abstentions,
            "candidate_coverage": self.candidate_coverage,
            "baseline_mae": self.baseline_mae,
            "candidate_mae": self.candidate_mae,
            "mae_delta": self.mae_delta,
            "baseline_accuracy": self.baseline_accuracy,
            "candidate_accuracy": self.candidate_accuracy,
            "accuracy_delta": self.accuracy_delta,
        }


@dataclass(frozen=True)
class ComparisonPacket:
    run_id: str
    correlation_id: str
    policy_id: str
    status: str
    recommendation: str
    overall_metrics: MetricSummary
    segment_metrics: Mapping[str, MetricSummary]
    blocking_reasons: Tuple[str, ...]
    review_reasons: Tuple[str, ...]
    operator_review_required: bool = True
    automatic_approval_allowed: bool = False
    automatic_promotion_allowed: bool = False
    automatic_baseline_replacement_allowed: bool = False
    paper_only: bool = True
    deterministic: bool = True

    def __post_init__(self) -> None:
        if self.status not in {"BLOCKED", "READY_FOR_OPERATOR_REVIEW"}:
            raise ValueError("invalid comparison status")
        if not self.operator_review_required:
            raise ValueError("operator review must remain required")
        prohibited = (
            self.automatic_approval_allowed,
            self.automatic_promotion_allowed,
            self.automatic_baseline_replacement_allowed,
        )
        if any(prohibited):
            raise ValueError("automatic authority escalation is prohibited")
        if not self.paper_only or not self.deterministic:
            raise ValueError("comparison must remain paper-only and deterministic")

    def as_dict(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "correlation_id": self.correlation_id,
            "policy_id": self.policy_id,
            "status": self.status,
            "recommendation": self.recommendation,
            "overall_metrics": self.overall_metrics.as_dict(),
            "segment_metrics": {
                key: value.as_dict()
                for key, value in sorted(self.segment_metrics.items())
            },
            "blocking_reasons": list(self.blocking_reasons),
            "review_reasons": list(self.review_reasons),
            "operator_review_required": self.operator_review_required,
            "automatic_approval_allowed": self.automatic_approval_allowed,
            "automatic_promotion_allowed": self.automatic_promotion_allowed,
            "automatic_baseline_replacement_allowed": (
                self.automatic_baseline_replacement_allowed
            ),
            "paper_only": self.paper_only,
            "deterministic": self.deterministic,
        }


def _classification_accuracy(
    values: Sequence[tuple[float, float]],
) -> float:
    if not values:
        return 0.0
    correct = sum(
        int((score >= 0.5) == (actual >= 0.5))
        for score, actual in values
    )
    return _rounded(correct / len(values))


def _mae(values: Sequence[tuple[float, float]]) -> float:
    if not values:
        return 0.0
    return _rounded(
        fsum(abs(score - actual) for score, actual in values) / len(values)
    )


def summarize_metrics(samples: Iterable[ValidationSample]) -> MetricSummary:
    materialized = tuple(samples)
    eligible = tuple(sample for sample in materialized if sample.eligible)
    candidate_scored = tuple(
        sample for sample in eligible if sample.candidate_score is not None
    )
    baseline_values = tuple(
        (sample.baseline_score, sample.actual_outcome)
        for sample in eligible
    )
    candidate_values = tuple(
        (float(sample.candidate_score), sample.actual_outcome)
        for sample in candidate_scored
    )

    baseline_mae = _mae(baseline_values)
    candidate_mae = _mae(candidate_values)
    baseline_accuracy = _classification_accuracy(baseline_values)
    candidate_accuracy = _classification_accuracy(candidate_values)
    coverage = (
        _rounded(len(candidate_scored) / len(eligible))
        if eligible
        else 0.0
    )

    return MetricSummary(
        total_samples=len(materialized),
        eligible_samples=len(eligible),
        excluded_samples=len(materialized) - len(eligible),
        candidate_scored_samples=len(candidate_scored),
        candidate_abstentions=len(eligible) - len(candidate_scored),
        candidate_coverage=coverage,
        baseline_mae=baseline_mae,
        candidate_mae=candidate_mae,
        mae_delta=_rounded(candidate_mae - baseline_mae),
        baseline_accuracy=baseline_accuracy,
        candidate_accuracy=candidate_accuracy,
        accuracy_delta=_rounded(candidate_accuracy - baseline_accuracy),
    )


def _segment_map(
    samples: Sequence[ValidationSample],
) -> dict[str, Tuple[ValidationSample, ...]]:
    segments: dict[str, list[ValidationSample]] = {}
    for sample in samples:
        segments.setdefault(sample.segment, []).append(sample)
    return {
        segment: tuple(items)
        for segment, items in sorted(segments.items())
    }


def evaluate_candidate(
    *,
    run_id: str,
    correlation_id: str,
    samples: Sequence[ValidationSample],
    policy: ComparisonPolicy,
) -> ComparisonPacket:
    materialized = tuple(samples)
    overall = summarize_metrics(materialized)
    by_segment = _segment_map(materialized)
    segment_metrics = {
        segment: summarize_metrics(items)
        for segment, items in by_segment.items()
    }

    blocking: list[str] = []
    review: list[str] = []

    if overall.eligible_samples < policy.minimum_eligible_samples:
        blocking.append("INSUFFICIENT_ELIGIBLE_SAMPLES")

    if overall.candidate_coverage < policy.minimum_candidate_coverage:
        blocking.append("INSUFFICIENT_CANDIDATE_COVERAGE")

    if (
        overall.candidate_scored_samples > 0
        and overall.mae_delta > policy.maximum_mae_regression
    ):
        blocking.append("OVERALL_MAE_REGRESSION")

    if (
        overall.candidate_scored_samples > 0
        and overall.accuracy_delta < policy.minimum_accuracy_delta
    ):
        blocking.append("OVERALL_ACCURACY_DELTA_BELOW_POLICY")

    for segment in policy.required_segments:
        summary = segment_metrics.get(segment)
        if summary is None:
            blocking.append(f"MISSING_REQUIRED_SEGMENT:{segment}")
            continue
        if summary.eligible_samples < policy.minimum_segment_samples:
            blocking.append(f"INSUFFICIENT_SEGMENT_SAMPLES:{segment}")
        if (
            summary.candidate_scored_samples > 0
            and summary.mae_delta > policy.maximum_segment_mae_regression
        ):
            blocking.append(f"SEGMENT_MAE_REGRESSION:{segment}")

    if overall.excluded_samples:
        review.append("EXCLUDED_SAMPLES_PRESENT")
    if overall.candidate_abstentions:
        review.append("CANDIDATE_ABSTENTIONS_PRESENT")
    if not blocking:
        review.append("OPERATOR_DECISION_REQUIRED")

    status = "BLOCKED" if blocking else "READY_FOR_OPERATOR_REVIEW"
    recommendation = (
        "DO_NOT_ADVANCE"
        if blocking
        else "CANDIDATE_MAY_PROCEED_TO_OPERATOR_REVIEW"
    )

    return ComparisonPacket(
        run_id=run_id,
        correlation_id=correlation_id,
        policy_id=policy.policy_id,
        status=status,
        recommendation=recommendation,
        overall_metrics=overall,
        segment_metrics=segment_metrics,
        blocking_reasons=tuple(sorted(set(blocking))),
        review_reasons=tuple(sorted(set(review))),
    )
