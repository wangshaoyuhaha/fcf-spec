from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal
from types import MappingProxyType
from typing import Any, Mapping

from .contracts import BacktestResult, freeze, identifier, utc_time


_CANDIDATE_TYPES = {
    "model-role-assignment",
    "fallback-model",
    "prompt",
    "data-source-policy",
    "factor",
    "strategy-configuration",
    "portfolio-control",
    "timeout-retry",
    "market-adapter-rule",
}
_QUALIFICATION_CHECKS = (
    "no-core-mutation",
    "no-p48",
    "no-hard-policy-conflict",
    "authorized-data-source",
    "licensed-data-use",
    "authorized-processing",
    "no-future-data-dependency",
    "no-hidden-risk-change",
    "no-hidden-benchmark-change",
    "no-hidden-cost-change",
    "no-undeclared-model-prompt-change",
    "no-undeclared-market-rule-change",
    "no-real-execution-path",
    "no-automatic-promotion-authority",
)
EVOLUTION_GATE_CHECKS = (
    "static-eligibility-review",
    "hard-policy-review",
    "data-license-review",
    "future-information-review",
    "declared-difference-review",
    "historical-backtesting",
    "independent-out-of-sample-testing",
    "walk-forward-testing",
    "regime-testing",
    "cost-liquidity-testing",
    "bias-review",
    "counterfactual-robustness-testing",
    "champion-comparison",
    "risk-review",
    "explicit-operator-approval",
    "versioned-activation-plan",
    "post-activation-monitoring-plan",
    "rollback-readiness",
)


@dataclass(frozen=True)
class HumanFeedback:
    feedback_id: str
    operator_id: str
    target_artifact_id: str
    classification: str
    reason: str
    submitted_at_utc: str

    def __post_init__(self) -> None:
        for field_name in (
            "feedback_id",
            "operator_id",
            "target_artifact_id",
            "classification",
        ):
            object.__setattr__(
                self,
                field_name,
                identifier(getattr(self, field_name), field_name),
            )
        utc_time(self.submitted_at_utc, "submitted_at_utc")
        if not self.reason.strip():
            raise ValueError("human feedback reason is required")


@dataclass(frozen=True)
class LearningCandidate:
    candidate_id: str
    candidate_type: str
    champion_version: str
    proposed_version: str
    source_result_ids: tuple[str, ...]
    source_feedback_ids: tuple[str, ...]
    declared_changes: Mapping[str, Any]
    rationale: str
    candidate_only: bool = True
    automatic_activation_allowed: bool = False

    def __post_init__(self) -> None:
        for field_name in ("candidate_id", "champion_version", "proposed_version"):
            object.__setattr__(
                self,
                field_name,
                identifier(getattr(self, field_name), field_name),
            )
        if self.candidate_type not in _CANDIDATE_TYPES:
            raise ValueError("unsupported learning candidate type")
        if self.champion_version == self.proposed_version:
            raise ValueError("Challenger must propose a new version")
        if not self.source_result_ids or not self.rationale.strip():
            raise ValueError("candidate evidence and rationale are required")
        if not self.declared_changes:
            raise ValueError("candidate must declare configuration changes")
        object.__setattr__(
            self,
            "source_result_ids",
            tuple(sorted({identifier(item, "source_result_id") for item in self.source_result_ids})),
        )
        object.__setattr__(
            self,
            "source_feedback_ids",
            tuple(sorted({identifier(item, "source_feedback_id") for item in self.source_feedback_ids})),
        )
        object.__setattr__(self, "declared_changes", freeze(self.declared_changes))
        if not self.candidate_only or self.automatic_activation_allowed:
            raise ValueError("learning output must remain a candidate")


@dataclass(frozen=True)
class QualificationRecord:
    candidate_id: str
    accepted: bool
    checks: Mapping[str, bool]
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "checks", freeze(self.checks))
        object.__setattr__(self, "reason_codes", tuple(sorted(set(self.reason_codes))))


@dataclass(frozen=True)
class ChampionChallengerExperiment:
    experiment_id: str
    candidate: LearningCandidate
    qualification: QualificationRecord
    champion_result: BacktestResult
    challenger_result: BacktestResult
    changed_variables: tuple[str, ...]
    experiment_label: str
    status: str
    metric_deltas: Mapping[str, Decimal]
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "experiment_id",
            identifier(self.experiment_id, "experiment_id"),
        )
        object.__setattr__(self, "metric_deltas", freeze(self.metric_deltas))
        if self.experiment_label not in {
            "SINGLE_VARIABLE",
            "COMPOUND_EXPERIMENT",
        }:
            raise ValueError("unsupported experiment label")
        if not self.operator_review_required:
            raise ValueError("experiment requires Operator review")


@dataclass(frozen=True)
class EvolutionGateDecision:
    experiment_id: str
    status: str
    gate_checks: Mapping[str, bool]
    reason_codes: tuple[str, ...]
    proposed_version: str
    rollback_version: str
    audit_sha256: str
    explicit_operator_approval_recorded: bool
    automatic_activation_allowed: bool = False
    automatic_rollback_allowed: bool = False
    champion_overwritten: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "gate_checks", freeze(self.gate_checks))
        if (
            self.automatic_activation_allowed
            or self.automatic_rollback_allowed
            or self.champion_overwritten
        ):
            raise ValueError("evolution gate cannot activate changes")


class ControlledEvolutionService:
    def qualify(
        self,
        candidate: LearningCandidate,
        checks: Mapping[str, bool],
    ) -> QualificationRecord:
        normalized = {name: checks.get(name) is True for name in _QUALIFICATION_CHECKS}
        reasons = tuple(name for name, passed in normalized.items() if not passed)
        return QualificationRecord(
            candidate_id=candidate.candidate_id,
            accepted=not reasons,
            checks=MappingProxyType(normalized),
            reason_codes=reasons,
        )

    def experiment(
        self,
        experiment_id: str,
        candidate: LearningCandidate,
        qualification: QualificationRecord,
        champion_result: BacktestResult,
        challenger_result: BacktestResult,
    ) -> ChampionChallengerExperiment:
        changed = tuple(sorted(candidate.declared_changes))
        champion_return = champion_result.metrics["mean_net_return"]
        challenger_return = challenger_result.metrics["mean_net_return"]
        champion_error = champion_result.metrics["mean_absolute_error"]
        challenger_error = challenger_result.metrics["mean_absolute_error"]
        deltas = MappingProxyType(
            {
                "mean_absolute_error": challenger_error - champion_error,
                "mean_net_return": challenger_return - champion_return,
            }
        )
        status = (
            "QUALIFICATION_REJECTED"
            if not qualification.accepted
            else (
                "CHALLENGER_OUTPERFORMED"
                if deltas["mean_net_return"] > 0
                and deltas["mean_absolute_error"] <= 0
                else "CHALLENGER_NOT_BETTER"
            )
        )
        return ChampionChallengerExperiment(
            experiment_id=experiment_id,
            candidate=candidate,
            qualification=qualification,
            champion_result=champion_result,
            challenger_result=challenger_result,
            changed_variables=changed,
            experiment_label=(
                "SINGLE_VARIABLE" if len(changed) == 1 else "COMPOUND_EXPERIMENT"
            ),
            status=status,
            metric_deltas=deltas,
        )

    def gate(
        self,
        experiment: ChampionChallengerExperiment,
        checks: Mapping[str, bool],
    ) -> EvolutionGateDecision:
        normalized = {name: checks.get(name) is True for name in EVOLUTION_GATE_CHECKS}
        reasons = [name for name, passed in normalized.items() if not passed]
        if experiment.status != "CHALLENGER_OUTPERFORMED":
            reasons.append("challenger-did-not-outperform")
        eligible = not reasons
        payload = {
            "checks": normalized,
            "experiment_id": experiment.experiment_id,
            "proposed_version": experiment.candidate.proposed_version,
            "reasons": sorted(reasons),
            "rollback_version": experiment.candidate.champion_version,
            "status": (
                "ELIGIBLE_FOR_OPERATOR_REVIEW"
                if eligible
                else "BLOCKED_REVIEW_REQUIRED"
            ),
        }
        audit_sha256 = hashlib.sha256(
            json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("ascii")
        ).hexdigest()
        return EvolutionGateDecision(
            experiment_id=experiment.experiment_id,
            status=payload["status"],
            gate_checks=MappingProxyType(normalized),
            reason_codes=tuple(reasons),
            proposed_version=experiment.candidate.proposed_version,
            rollback_version=experiment.candidate.champion_version,
            audit_sha256=audit_sha256,
            explicit_operator_approval_recorded=normalized[
                "explicit-operator-approval"
            ],
        )
