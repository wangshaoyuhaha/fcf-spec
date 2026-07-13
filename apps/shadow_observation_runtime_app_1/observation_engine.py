from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from .domain import ObservationRecord
from .input_loader import LoadedObservationDataset


@dataclass(frozen=True)
class ObservationMetricSummary:
    total_records: int
    observed_outcomes: int
    candidate_observations: int
    candidate_coverage: float
    baseline_mae: Optional[float]
    candidate_mae: Optional[float]
    candidate_mae_delta: Optional[float]
    risk_flag_count: int
    contradiction_count: int


@dataclass(frozen=True)
class SegmentObservationSummary:
    segment: str
    observed_outcomes: int
    candidate_observations: int
    candidate_coverage: float
    baseline_mae: Optional[float]
    candidate_mae: Optional[float]
    candidate_mae_delta: Optional[float]


@dataclass(frozen=True)
class ShadowObservationPacket:
    run_id: str
    correlation_id: str
    artifact_id: str
    artifact_version: str
    window_id: str
    status: str
    summary: ObservationMetricSummary
    segments: Tuple[SegmentObservationSummary, ...]
    blockers: Tuple[str, ...]
    warnings: Tuple[str, ...]
    risk_flags: Tuple[str, ...]
    contradiction_evidence: Tuple[str, ...]
    operator_review_required: bool = True
    deterministic_authority: bool = True
    ai_advisory_only: bool = True
    automatic_approval_allowed: bool = False
    automatic_promotion_allowed: bool = False
    automatic_baseline_replacement_allowed: bool = False

    def __post_init__(self) -> None:
        if self.status not in {
            "BLOCKED",
            "DEGRADED",
            "REVIEW_REQUIRED",
        }:
            raise ValueError("invalid shadow observation status")
        if not self.operator_review_required:
            raise ValueError("operator review must remain required")
        if not self.deterministic_authority:
            raise ValueError("deterministic authority must remain enabled")
        if not self.ai_advisory_only:
            raise ValueError("AI must remain advisory only")
        if (
            self.automatic_approval_allowed
            or self.automatic_promotion_allowed
            or self.automatic_baseline_replacement_allowed
        ):
            raise ValueError("automatic governance actions are prohibited")


def _unique(values: list[str]) -> Tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _mae(
    records: Tuple[ObservationRecord, ...],
    score_field: str,
) -> Optional[float]:
    errors = []
    for record in records:
        outcome = record.actual_outcome
        score = getattr(record, score_field)
        if outcome is None or score is None:
            continue
        errors.append(abs(float(score) - float(outcome)))
    if not errors:
        return None
    return sum(errors) / len(errors)


def _segment_summary(
    segment: str,
    records: Tuple[ObservationRecord, ...],
) -> SegmentObservationSummary:
    observed = tuple(
        record
        for record in records
        if record.actual_outcome is not None
    )
    candidate = tuple(
        record
        for record in observed
        if record.candidate_score is not None
    )
    baseline_mae = _mae(observed, "baseline_score")
    candidate_mae = _mae(observed, "candidate_score")
    delta = (
        None
        if baseline_mae is None or candidate_mae is None
        else candidate_mae - baseline_mae
    )
    coverage = (
        0.0
        if not observed
        else len(candidate) / len(observed)
    )
    return SegmentObservationSummary(
        segment=segment,
        observed_outcomes=len(observed),
        candidate_observations=len(candidate),
        candidate_coverage=coverage,
        baseline_mae=baseline_mae,
        candidate_mae=candidate_mae,
        candidate_mae_delta=delta,
    )


def evaluate_shadow_observation(
    dataset: LoadedObservationDataset,
) -> ShadowObservationPacket:
    request = dataset.request
    policy = request.policy
    records = dataset.records

    observed = tuple(
        record
        for record in records
        if record.actual_outcome is not None
    )
    candidate = tuple(
        record
        for record in observed
        if record.candidate_score is not None
    )

    baseline_mae = _mae(observed, "baseline_score")
    candidate_mae = _mae(observed, "candidate_score")
    candidate_delta = (
        None
        if baseline_mae is None or candidate_mae is None
        else candidate_mae - baseline_mae
    )
    candidate_coverage = (
        0.0
        if not observed
        else len(candidate) / len(observed)
    )

    risk_flags = _unique(
        [
            flag
            for record in records
            for flag in record.risk_flags
        ]
    )
    contradictions = _unique(
        [
            evidence
            for record in records
            for evidence in record.contradiction_evidence
        ]
    )

    segment_names = tuple(
        dict.fromkeys(record.segment for record in records)
    )
    segments = tuple(
        _segment_summary(
            segment,
            tuple(
                record
                for record in records
                if record.segment == segment
            ),
        )
        for segment in segment_names
    )
    segment_map = {
        summary.segment: summary
        for summary in segments
    }

    blockers: list[str] = []
    warnings: list[str] = []

    if len(observed) < policy.minimum_observed_outcomes:
        blockers.append("minimum_observed_outcomes_not_met")

    for required_segment in policy.required_segments:
        summary = segment_map.get(required_segment)
        if summary is None:
            blockers.append(
                f"required_segment_missing:{required_segment}"
            )
            continue
        if summary.observed_outcomes < policy.minimum_segment_outcomes:
            blockers.append(
                f"minimum_segment_outcomes_not_met:{required_segment}"
            )

    if candidate_coverage < policy.minimum_candidate_coverage:
        warnings.append("minimum_candidate_coverage_not_met")

    if candidate_mae is None:
        warnings.append("candidate_outcomes_unavailable")
    elif (
        candidate_delta is not None
        and candidate_delta
        > policy.maximum_candidate_mae_regression
    ):
        warnings.append("candidate_mae_regression_exceeded")

    for summary in segments:
        if (
            summary.candidate_mae_delta is not None
            and summary.candidate_mae_delta
            > policy.maximum_segment_mae_regression
        ):
            warnings.append(
                f"segment_mae_regression_exceeded:{summary.segment}"
            )

    if risk_flags:
        warnings.append("risk_flags_present")
    if contradictions:
        warnings.append("contradiction_evidence_present")

    blockers_tuple = _unique(blockers)
    warnings_tuple = _unique(warnings)

    if blockers_tuple:
        status = "BLOCKED"
    elif warnings_tuple:
        status = "DEGRADED"
    else:
        status = "REVIEW_REQUIRED"

    summary = ObservationMetricSummary(
        total_records=len(records),
        observed_outcomes=len(observed),
        candidate_observations=len(candidate),
        candidate_coverage=candidate_coverage,
        baseline_mae=baseline_mae,
        candidate_mae=candidate_mae,
        candidate_mae_delta=candidate_delta,
        risk_flag_count=len(risk_flags),
        contradiction_count=len(contradictions),
    )

    return ShadowObservationPacket(
        run_id=request.run_id,
        correlation_id=request.correlation_id,
        artifact_id=request.artifact.artifact_id,
        artifact_version=request.artifact.artifact_version,
        window_id=request.window.window_id,
        status=status,
        summary=summary,
        segments=segments,
        blockers=blockers_tuple,
        warnings=warnings_tuple,
        risk_flags=risk_flags,
        contradiction_evidence=contradictions,
    )
