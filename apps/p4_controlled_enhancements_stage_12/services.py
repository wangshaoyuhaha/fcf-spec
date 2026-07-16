from __future__ import annotations

from decimal import Decimal

from apps.controlled_learning_backtesting_p0_p3_stage_11 import LearningCandidate

from .boundary import P4_CONTROLLED_ENHANCEMENTS_BOUNDARY
from .contracts import (
    CaseMemoryQuery,
    CaseMemoryRecord,
    CaseMemoryRetrieval,
    ChallengerProposalRequest,
    ExperimentScheduleProposal,
    ForwardShadowObservation,
    RealtimeShadowValidation,
    RegisteredTrainingResult,
    SpecialistTrainingEvaluation,
    SpecialistTrainingPlan,
)
from apps.controlled_learning_backtesting_p0_p3_stage_11.contracts import utc_time


class RegisteredCaseMemoryService:
    def retrieve(
        self,
        records: tuple[CaseMemoryRecord, ...],
        query: CaseMemoryQuery,
    ) -> CaseMemoryRetrieval:
        P4_CONTROLLED_ENHANCEMENTS_BOUNDARY.__post_init__()
        case_ids = tuple(item.case_id for item in records)
        if len(set(case_ids)) != len(case_ids):
            raise ValueError("registered case ids must be unique")
        as_of = utc_time(query.as_of_time_utc, "as_of_time_utc")
        allowed = set(query.allowed_artifact_ids)
        eligible = []
        reasons = []
        for record in records:
            if utc_time(record.available_at_utc, "available_at_utc") > as_of:
                reasons.append("future-case-excluded")
                continue
            if not set(record.source_artifact_ids).issubset(allowed):
                reasons.append("unregistered-scope-case-excluded")
                continue
            if query.market_id is not None and record.market_id is not query.market_id:
                continue
            if query.regime_id is not None and record.regime_id != query.regime_id:
                continue
            eligible.append(record)
        eligible.sort(
            key=lambda item: (
                utc_time(item.available_at_utc, "available_at_utc"),
                item.case_id,
            ),
            reverse=True,
        )
        return CaseMemoryRetrieval(
            query_id=query.query_id,
            records=tuple(eligible[: query.limit]),
            reason_codes=tuple(reasons),
        )


class DeterministicP4ProposalService:
    def propose_challenger(
        self,
        request: ChallengerProposalRequest,
    ) -> LearningCandidate:
        P4_CONTROLLED_ENHANCEMENTS_BOUNDARY.__post_init__()
        declared_changes = {}
        for offset, key in enumerate(sorted(request.change_space)):
            options = request.change_space[key]
            declared_changes[key] = options[
                (request.deterministic_seed + offset) % len(options)
            ]
        return LearningCandidate(
            candidate_id=f"candidate-{request.proposal_id}",
            candidate_type=request.candidate_type,
            champion_version=request.champion_version,
            proposed_version=request.proposed_version,
            source_result_ids=request.source_result_ids,
            source_feedback_ids=request.source_feedback_ids,
            declared_changes=declared_changes,
            rationale=request.rationale,
        )

    def propose_schedule(
        self,
        schedule_id: str,
        candidate: LearningCandidate,
        proposed_start_utc: str,
        proposed_end_utc: str,
        dependency_artifact_ids: tuple[str, ...],
        registered_artifact_ids: tuple[str, ...],
    ) -> ExperimentScheduleProposal:
        P4_CONTROLLED_ENHANCEMENTS_BOUNDARY.__post_init__()
        registered = set(registered_artifact_ids)
        if not set(dependency_artifact_ids).issubset(registered):
            raise ValueError("schedule dependency is not registered")
        return ExperimentScheduleProposal(
            schedule_id=schedule_id,
            candidate_id=candidate.candidate_id,
            proposed_start_utc=proposed_start_utc,
            proposed_end_utc=proposed_end_utc,
            dependency_artifact_ids=dependency_artifact_ids,
        )


class LocalForwardShadowValidationService:
    def evaluate(
        self,
        observations: tuple[ForwardShadowObservation, ...],
        as_of_time_utc: str,
    ) -> RealtimeShadowValidation:
        P4_CONTROLLED_ENHANCEMENTS_BOUNDARY.__post_init__()
        as_of = utc_time(as_of_time_utc, "as_of_time_utc")
        errors = []
        direction_matches = []
        reasons = []
        blocked = not observations
        if not observations:
            reasons.append("shadow-observations-required")
        for item in observations:
            if utc_time(item.registered_at_utc, "registered_at_utc") > as_of:
                reasons.append("future-registration-blocked")
                blocked = True
                continue
            if item.observed_return is None:
                reasons.append("shadow-observation-pending")
                continue
            error = item.observed_return - item.expected_return
            errors.append(error)
            direction_matches.append(
                item.expected_return == 0
                or item.observed_return == 0
                or (item.expected_return > 0) == (item.observed_return > 0)
            )
            if (
                item.expected_return != 0
                and item.observed_return != 0
                and (item.expected_return > 0) != (item.observed_return > 0)
            ):
                reasons.append("shadow-direction-contradiction")
        mean_error = (
            sum(errors, Decimal("0")) / Decimal(len(errors)) if errors else None
        )
        mean_absolute_error = (
            sum((abs(value) for value in errors), Decimal("0"))
            / Decimal(len(errors))
            if errors
            else None
        )
        direction_accuracy = (
            Decimal(sum(direction_matches)) / Decimal(len(direction_matches))
            if direction_matches
            else None
        )
        status = (
            "BLOCKED_REVIEW_REQUIRED"
            if blocked
            else (
                "DEGRADED_REVIEW_REQUIRED"
                if reasons
                else "PASS_REVIEW_REQUIRED"
            )
        )
        return RealtimeShadowValidation(
            as_of_time_utc=as_of_time_utc,
            observation_count=len(observations),
            mature_count=len(errors),
            mean_error=mean_error,
            mean_absolute_error=mean_absolute_error,
            direction_accuracy=direction_accuracy,
            reason_codes=tuple(reasons),
            status=status,
        )


class SpecialistTrainingGovernanceService:
    def evaluate_registered_result(
        self,
        plan: SpecialistTrainingPlan,
        result: RegisteredTrainingResult,
    ) -> SpecialistTrainingEvaluation:
        P4_CONTROLLED_ENHANCEMENTS_BOUNDARY.__post_init__()
        reasons = []
        if result.plan_id != plan.plan_id:
            reasons.append("training-plan-result-mismatch")
        if utc_time(result.registered_at_utc, "registered_at_utc") < utc_time(
            plan.as_of_time_utc,
            "as_of_time_utc",
        ):
            reasons.append("training-result-precedes-plan")
        missing = set(plan.objective_metrics) - set(result.metrics)
        if missing:
            reasons.append("objective-metrics-missing")
        if any(value < 0 for value in result.metrics.values()):
            reasons.append("negative-training-metric")
        if not set(result.source_evidence_ids).issubset(plan.dataset_artifact_ids):
            reasons.append("training-result-source-outside-plan")
        status = (
            "BLOCKED_REVIEW_REQUIRED"
            if {
                "training-plan-result-mismatch",
                "training-result-precedes-plan",
                "training-result-source-outside-plan",
            }.intersection(reasons)
            else (
                "DEGRADED_REVIEW_REQUIRED"
                if reasons
                else "PASS_REVIEW_REQUIRED"
            )
        )
        return SpecialistTrainingEvaluation(
            plan_id=plan.plan_id,
            result_id=result.result_id,
            status=status,
            reason_codes=tuple(reasons),
        )
