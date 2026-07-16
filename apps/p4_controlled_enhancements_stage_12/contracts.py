from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping

from apps.controlled_learning_backtesting_p0_p3_stage_11.contracts import (
    decimal_value,
    freeze,
    identifier,
    utc_time,
)
from apps.multi_market_adapters_stage_6 import MarketAdapterId


def _identifiers(values: tuple[str, ...], field_name: str) -> tuple[str, ...]:
    normalized = tuple(sorted({identifier(item, field_name) for item in values}))
    if not normalized:
        raise ValueError(f"{field_name} values are required")
    return normalized


@dataclass(frozen=True)
class CaseMemoryRecord:
    case_id: str
    available_at_utc: str
    market_id: MarketAdapterId
    regime_id: str
    outcome_status: str
    source_artifact_ids: tuple[str, ...]
    attributes: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "case_id", identifier(self.case_id, "case_id"))
        utc_time(self.available_at_utc, "available_at_utc")
        object.__setattr__(self, "market_id", MarketAdapterId(self.market_id))
        object.__setattr__(self, "regime_id", identifier(self.regime_id, "regime_id"))
        if self.outcome_status not in {
            "POSITIVE",
            "NEGATIVE",
            "BLOCKED",
            "FAILED",
            "INCONCLUSIVE",
        }:
            raise ValueError("unsupported case outcome_status")
        object.__setattr__(
            self,
            "source_artifact_ids",
            _identifiers(self.source_artifact_ids, "source_artifact_id"),
        )
        object.__setattr__(self, "attributes", freeze(self.attributes))


@dataclass(frozen=True)
class CaseMemoryQuery:
    query_id: str
    as_of_time_utc: str
    market_id: MarketAdapterId | None
    regime_id: str | None
    allowed_artifact_ids: tuple[str, ...]
    limit: int = 20

    def __post_init__(self) -> None:
        object.__setattr__(self, "query_id", identifier(self.query_id, "query_id"))
        utc_time(self.as_of_time_utc, "as_of_time_utc")
        if self.market_id is not None:
            object.__setattr__(self, "market_id", MarketAdapterId(self.market_id))
        if self.regime_id is not None:
            object.__setattr__(self, "regime_id", identifier(self.regime_id, "regime_id"))
        object.__setattr__(
            self,
            "allowed_artifact_ids",
            _identifiers(self.allowed_artifact_ids, "allowed_artifact_id"),
        )
        if isinstance(self.limit, bool) or not 1 <= self.limit <= 100:
            raise ValueError("case-memory limit must be between 1 and 100")


@dataclass(frozen=True)
class CaseMemoryRetrieval:
    query_id: str
    records: tuple[CaseMemoryRecord, ...]
    reason_codes: tuple[str, ...]
    read_only: bool = True
    point_in_time_enforced: bool = True
    network_access_used: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "records", tuple(self.records))
        object.__setattr__(self, "reason_codes", tuple(sorted(set(self.reason_codes))))
        if not self.read_only or not self.point_in_time_enforced or self.network_access_used:
            raise ValueError("case-memory retrieval authority boundary failed")


@dataclass(frozen=True)
class ChallengerProposalRequest:
    proposal_id: str
    candidate_type: str
    champion_version: str
    proposed_version: str
    source_result_ids: tuple[str, ...]
    source_feedback_ids: tuple[str, ...]
    change_space: Mapping[str, tuple[Any, ...]]
    rationale: str
    deterministic_seed: int

    def __post_init__(self) -> None:
        for field_name in ("proposal_id", "champion_version", "proposed_version"):
            object.__setattr__(self, field_name, identifier(getattr(self, field_name), field_name))
        object.__setattr__(
            self,
            "source_result_ids",
            _identifiers(self.source_result_ids, "source_result_id"),
        )
        object.__setattr__(
            self,
            "source_feedback_ids",
            tuple(sorted({identifier(item, "source_feedback_id") for item in self.source_feedback_ids})),
        )
        normalized = {
            identifier(key, "change_key"): tuple(freeze(item) for item in values)
            for key, values in self.change_space.items()
        }
        if not normalized or any(not values for values in normalized.values()):
            raise ValueError("change_space requires non-empty options")
        object.__setattr__(self, "change_space", freeze(normalized))
        if not self.rationale.strip():
            raise ValueError("Challenger proposal rationale is required")
        if isinstance(self.deterministic_seed, bool) or self.deterministic_seed < 0:
            raise ValueError("deterministic_seed must be non-negative")


@dataclass(frozen=True)
class ExperimentScheduleProposal:
    schedule_id: str
    candidate_id: str
    proposed_start_utc: str
    proposed_end_utc: str
    dependency_artifact_ids: tuple[str, ...]
    status: str = "PROPOSED_REVIEW_REQUIRED"
    operator_review_required: bool = True
    job_execution_allowed: bool = False

    def __post_init__(self) -> None:
        for field_name in ("schedule_id", "candidate_id"):
            object.__setattr__(self, field_name, identifier(getattr(self, field_name), field_name))
        start = utc_time(self.proposed_start_utc, "proposed_start_utc")
        end = utc_time(self.proposed_end_utc, "proposed_end_utc")
        if end <= start:
            raise ValueError("experiment schedule must have positive duration")
        object.__setattr__(
            self,
            "dependency_artifact_ids",
            _identifiers(self.dependency_artifact_ids, "dependency_artifact_id"),
        )
        if self.status != "PROPOSED_REVIEW_REQUIRED":
            raise ValueError("experiment schedule must remain a proposal")
        if not self.operator_review_required or self.job_execution_allowed:
            raise ValueError("experiment schedule cannot execute jobs")


@dataclass(frozen=True)
class ForwardShadowObservation:
    observation_id: str
    market_id: MarketAdapterId
    forward_window_started_at_utc: str
    decision_time_utc: str
    observation_time_utc: str
    registered_at_utc: str
    expected_return: Decimal
    observed_return: Decimal | None
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "observation_id", identifier(self.observation_id, "observation_id"))
        object.__setattr__(self, "market_id", MarketAdapterId(self.market_id))
        start = utc_time(self.forward_window_started_at_utc, "forward_window_started_at_utc")
        decision = utc_time(self.decision_time_utc, "decision_time_utc")
        observation = utc_time(self.observation_time_utc, "observation_time_utc")
        registered = utc_time(self.registered_at_utc, "registered_at_utc")
        if decision < start or observation < decision or registered < observation:
            raise ValueError("Shadow observation is not forward-only")
        object.__setattr__(self, "expected_return", decimal_value(self.expected_return, "expected_return"))
        if self.observed_return is not None:
            object.__setattr__(self, "observed_return", decimal_value(self.observed_return, "observed_return"))
        object.__setattr__(self, "evidence_ids", _identifiers(self.evidence_ids, "evidence_id"))


@dataclass(frozen=True)
class RealtimeShadowValidation:
    as_of_time_utc: str
    observation_count: int
    mature_count: int
    mean_error: Decimal | None
    reason_codes: tuple[str, ...]
    status: str
    network_access_used: bool = False
    real_execution_used: bool = False
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        utc_time(self.as_of_time_utc, "as_of_time_utc")
        object.__setattr__(self, "reason_codes", tuple(sorted(set(self.reason_codes))))
        if self.status not in {"PASS_REVIEW_REQUIRED", "DEGRADED_REVIEW_REQUIRED", "BLOCKED_REVIEW_REQUIRED"}:
            raise ValueError("unsupported Shadow validation status")
        if self.network_access_used or self.real_execution_used or not self.operator_review_required:
            raise ValueError("Shadow validation authority boundary failed")


@dataclass(frozen=True)
class SpecialistTrainingPlan:
    plan_id: str
    specialist_role: str
    as_of_time_utc: str
    dataset_artifact_ids: tuple[str, ...]
    config_snapshot_id: str
    objective_metrics: tuple[str, ...]
    operator_trigger_id: str
    training_execution_allowed: bool = False

    def __post_init__(self) -> None:
        for field_name in ("plan_id", "specialist_role", "config_snapshot_id", "operator_trigger_id"):
            object.__setattr__(self, field_name, identifier(getattr(self, field_name), field_name))
        utc_time(self.as_of_time_utc, "as_of_time_utc")
        object.__setattr__(self, "dataset_artifact_ids", _identifiers(self.dataset_artifact_ids, "dataset_artifact_id"))
        object.__setattr__(self, "objective_metrics", _identifiers(self.objective_metrics, "objective_metric"))
        if self.training_execution_allowed:
            raise ValueError("Stage 12 cannot execute specialist training")


@dataclass(frozen=True)
class RegisteredTrainingResult:
    result_id: str
    plan_id: str
    registered_at_utc: str
    training_artifact_id: str
    source_evidence_ids: tuple[str, ...]
    metrics: Mapping[str, Decimal]
    training_executed_by_stage_12: bool = False
    model_invocation_performed_by_stage_12: bool = False

    def __post_init__(self) -> None:
        for field_name in ("result_id", "plan_id", "training_artifact_id"):
            object.__setattr__(self, field_name, identifier(getattr(self, field_name), field_name))
        utc_time(self.registered_at_utc, "registered_at_utc")
        object.__setattr__(self, "source_evidence_ids", _identifiers(self.source_evidence_ids, "source_evidence_id"))
        metrics = {
            identifier(key, "metric_id"): decimal_value(value, "metric_value")
            for key, value in self.metrics.items()
        }
        if not metrics:
            raise ValueError("registered training metrics are required")
        object.__setattr__(self, "metrics", freeze(metrics))
        if self.training_executed_by_stage_12 or self.model_invocation_performed_by_stage_12:
            raise ValueError("Stage 12 may evaluate registered training results only")


@dataclass(frozen=True)
class SpecialistTrainingEvaluation:
    plan_id: str
    result_id: str
    status: str
    reason_codes: tuple[str, ...]
    advisory_only: bool = True
    operator_review_required: bool = True
    automatic_activation_allowed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "reason_codes", tuple(sorted(set(self.reason_codes))))
        if self.status not in {"PASS_REVIEW_REQUIRED", "DEGRADED_REVIEW_REQUIRED", "BLOCKED_REVIEW_REQUIRED"}:
            raise ValueError("unsupported specialist evaluation status")
        if not self.advisory_only or not self.operator_review_required or self.automatic_activation_allowed:
            raise ValueError("specialist evaluation cannot transition authority")
