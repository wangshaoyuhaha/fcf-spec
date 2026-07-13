from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Tuple

from .domain import ValidationRunRequest
from .input_loader import LoadedValidationDataset
from .metric_engine import ComparisonPacket


_ALLOWED_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


def _require_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


@dataclass(frozen=True)
class RiskFlag:
    code: str
    severity: str
    message: str
    blocking: bool
    source: str = "deterministic_validation_runtime"

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", _require_text(self.code, "code"))
        severity = _require_text(self.severity, "severity").upper()
        if severity not in _ALLOWED_SEVERITIES:
            raise ValueError("severity must be LOW, MEDIUM, HIGH, or CRITICAL")
        object.__setattr__(self, "severity", severity)
        object.__setattr__(self, "message", _require_text(self.message, "message"))
        object.__setattr__(self, "source", _require_text(self.source, "source"))

    def as_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "blocking": self.blocking,
            "source": self.source,
        }


@dataclass(frozen=True)
class ContradictionRecord:
    contradiction_id: str
    correlation_id: str
    category: str
    statement_a: str
    statement_b: str
    severity: str
    unresolved: bool = True
    evidence_ids: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        for field_name in (
            "contradiction_id",
            "correlation_id",
            "category",
            "statement_a",
            "statement_b",
        ):
            object.__setattr__(
                self,
                field_name,
                _require_text(getattr(self, field_name), field_name),
            )
        severity = _require_text(self.severity, "severity").upper()
        if severity not in _ALLOWED_SEVERITIES:
            raise ValueError("severity must be LOW, MEDIUM, HIGH, or CRITICAL")
        object.__setattr__(self, "severity", severity)
        normalized_evidence = tuple(
            _require_text(item, "evidence_id") for item in self.evidence_ids
        )
        if len(set(normalized_evidence)) != len(normalized_evidence):
            raise ValueError("evidence_ids must be unique")
        object.__setattr__(self, "evidence_ids", normalized_evidence)

    def as_dict(self) -> dict[str, object]:
        return {
            "contradiction_id": self.contradiction_id,
            "correlation_id": self.correlation_id,
            "category": self.category,
            "statement_a": self.statement_a,
            "statement_b": self.statement_b,
            "severity": self.severity,
            "unresolved": self.unresolved,
            "evidence_ids": list(self.evidence_ids),
        }


@dataclass(frozen=True)
class ValidationResultPacket:
    schema_version: str
    run_id: str
    correlation_id: str
    artifact_id: str
    artifact_version: str
    window_id: str
    policy_id: str
    status: str
    recommendation: str
    comparison: ComparisonPacket
    risk_flags: Tuple[RiskFlag, ...]
    contradictions: Tuple[ContradictionRecord, ...]
    operator_review_required: bool = True
    paper_only: bool = True
    deterministic_authority: bool = True
    immutable_evidence: bool = True
    automatic_approval_allowed: bool = False
    automatic_promotion_allowed: bool = False
    automatic_baseline_replacement_allowed: bool = False
    automatic_learning_activation_allowed: bool = False
    automatic_archive_allowed: bool = False
    real_execution_allowed: bool = False

    def __post_init__(self) -> None:
        if self.schema_version != "paper_validation_result_v1":
            raise ValueError("unsupported validation result schema")
        if self.status not in {"BLOCKED", "READY_FOR_OPERATOR_REVIEW"}:
            raise ValueError("invalid validation result status")
        if not self.operator_review_required:
            raise ValueError("operator review must remain required")
        if not self.paper_only or not self.deterministic_authority:
            raise ValueError("result must remain paper-only and deterministic")
        if not self.immutable_evidence:
            raise ValueError("validation evidence must remain immutable")
        prohibited = (
            self.automatic_approval_allowed,
            self.automatic_promotion_allowed,
            self.automatic_baseline_replacement_allowed,
            self.automatic_learning_activation_allowed,
            self.automatic_archive_allowed,
            self.real_execution_allowed,
        )
        if any(prohibited):
            raise ValueError("automatic or real-world authority is prohibited")
        if self.comparison.run_id != self.run_id:
            raise ValueError("comparison run_id mismatch")
        if self.comparison.correlation_id != self.correlation_id:
            raise ValueError("comparison correlation_id mismatch")
        if self.comparison.policy_id != self.policy_id:
            raise ValueError("comparison policy_id mismatch")
        for record in self.contradictions:
            if record.correlation_id != self.correlation_id:
                raise ValueError("contradiction correlation_id mismatch")

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "correlation_id": self.correlation_id,
            "artifact_id": self.artifact_id,
            "artifact_version": self.artifact_version,
            "window_id": self.window_id,
            "policy_id": self.policy_id,
            "status": self.status,
            "recommendation": self.recommendation,
            "comparison": self.comparison.as_dict(),
            "risk_flags": [item.as_dict() for item in self.risk_flags],
            "contradictions": [item.as_dict() for item in self.contradictions],
            "operator_review_required": self.operator_review_required,
            "paper_only": self.paper_only,
            "deterministic_authority": self.deterministic_authority,
            "immutable_evidence": self.immutable_evidence,
            "automatic_approval_allowed": self.automatic_approval_allowed,
            "automatic_promotion_allowed": self.automatic_promotion_allowed,
            "automatic_baseline_replacement_allowed": (
                self.automatic_baseline_replacement_allowed
            ),
            "automatic_learning_activation_allowed": (
                self.automatic_learning_activation_allowed
            ),
            "automatic_archive_allowed": self.automatic_archive_allowed,
            "real_execution_allowed": self.real_execution_allowed,
        }


@dataclass(frozen=True)
class OperatorReviewPacket:
    schema_version: str
    run_id: str
    correlation_id: str
    validation_status: str
    recommendation: str
    result_packet: ValidationResultPacket
    permitted_operator_actions: Tuple[str, ...]
    required_action: str
    operator_review_required: bool = True
    paper_only: bool = True
    automatic_decision_allowed: bool = False
    promotion_action_available: bool = False
    baseline_replacement_action_available: bool = False
    learning_activation_action_available: bool = False
    real_execution_action_available: bool = False

    def __post_init__(self) -> None:
        if self.schema_version != "paper_validation_operator_review_v1":
            raise ValueError("unsupported operator review schema")
        if not self.operator_review_required or not self.paper_only:
            raise ValueError("review packet must remain paper-only and review-gated")
        prohibited = (
            self.automatic_decision_allowed,
            self.promotion_action_available,
            self.baseline_replacement_action_available,
            self.learning_activation_action_available,
            self.real_execution_action_available,
        )
        if any(prohibited):
            raise ValueError("prohibited review action cannot be enabled")
        if self.result_packet.run_id != self.run_id:
            raise ValueError("result packet run_id mismatch")
        if self.result_packet.correlation_id != self.correlation_id:
            raise ValueError("result packet correlation_id mismatch")
        if self.result_packet.status != self.validation_status:
            raise ValueError("result packet status mismatch")
        if not self.permitted_operator_actions:
            raise ValueError("permitted_operator_actions must not be empty")

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "correlation_id": self.correlation_id,
            "validation_status": self.validation_status,
            "recommendation": self.recommendation,
            "result_packet": self.result_packet.as_dict(),
            "permitted_operator_actions": list(self.permitted_operator_actions),
            "required_action": self.required_action,
            "operator_review_required": self.operator_review_required,
            "paper_only": self.paper_only,
            "automatic_decision_allowed": self.automatic_decision_allowed,
            "promotion_action_available": self.promotion_action_available,
            "baseline_replacement_action_available": (
                self.baseline_replacement_action_available
            ),
            "learning_activation_action_available": (
                self.learning_activation_action_available
            ),
            "real_execution_action_available": self.real_execution_action_available,
        }


def derive_comparison_risk_flags(
    comparison: ComparisonPacket,
) -> Tuple[RiskFlag, ...]:
    flags: list[RiskFlag] = []
    for reason in comparison.blocking_reasons:
        flags.append(
            RiskFlag(
                code=reason,
                severity="HIGH",
                message=f"Blocking comparison condition: {reason}",
                blocking=True,
            )
        )
    for reason in comparison.review_reasons:
        flags.append(
            RiskFlag(
                code=reason,
                severity="MEDIUM",
                message=f"Operator review condition: {reason}",
                blocking=False,
            )
        )
    return tuple(flags)


def _deduplicate_risk_flags(flags: Iterable[RiskFlag]) -> Tuple[RiskFlag, ...]:
    result: list[RiskFlag] = []
    seen: set[tuple[str, str, str, bool, str]] = set()
    for flag in flags:
        identity = (
            flag.code,
            flag.severity,
            flag.message,
            flag.blocking,
            flag.source,
        )
        if identity not in seen:
            result.append(flag)
            seen.add(identity)
    return tuple(result)


def build_validation_result_packet(
    *,
    request: ValidationRunRequest,
    dataset: LoadedValidationDataset,
    comparison: ComparisonPacket,
    risk_flags: Iterable[RiskFlag] = (),
    contradictions: Iterable[ContradictionRecord] = (),
) -> ValidationResultPacket:
    if dataset.artifact.artifact_id != request.artifact_id:
        raise ValueError("dataset artifact_id mismatch")
    if dataset.artifact.artifact_version != request.artifact_version:
        raise ValueError("dataset artifact_version mismatch")
    if dataset.artifact.correlation_id != request.correlation_id:
        raise ValueError("dataset correlation_id mismatch")
    if dataset.window != request.window:
        raise ValueError("dataset evaluation window mismatch")

    materialized_contradictions = tuple(contradictions)
    combined_flags = _deduplicate_risk_flags(
        tuple(derive_comparison_risk_flags(comparison)) + tuple(risk_flags)
    )
    unresolved_blocking_contradiction = any(
        record.unresolved and record.severity in {"HIGH", "CRITICAL"}
        for record in materialized_contradictions
    )
    explicit_blocking_risk = any(flag.blocking for flag in combined_flags)
    blocked = (
        comparison.status == "BLOCKED"
        or explicit_blocking_risk
        or unresolved_blocking_contradiction
    )
    status = "BLOCKED" if blocked else "READY_FOR_OPERATOR_REVIEW"
    recommendation = (
        "DO_NOT_ADVANCE"
        if blocked
        else "CANDIDATE_MAY_PROCEED_TO_OPERATOR_REVIEW"
    )

    return ValidationResultPacket(
        schema_version="paper_validation_result_v1",
        run_id=request.run_id,
        correlation_id=request.correlation_id,
        artifact_id=request.artifact_id,
        artifact_version=request.artifact_version,
        window_id=request.window.window_id,
        policy_id=request.policy.policy_id,
        status=status,
        recommendation=recommendation,
        comparison=comparison,
        risk_flags=combined_flags,
        contradictions=materialized_contradictions,
    )


def build_operator_review_packet(
    result_packet: ValidationResultPacket,
) -> OperatorReviewPacket:
    if result_packet.status == "BLOCKED":
        actions = (
            "ACKNOWLEDGE_BLOCK",
            "REJECT_CANDIDATE",
            "REQUEST_REVISION",
        )
        required_action = "OPERATOR_REVIEW_BLOCKING_EVIDENCE"
    else:
        actions = (
            "ACKNOWLEDGE_RESULT",
            "REJECT_CANDIDATE",
            "REQUEST_REVISION",
            "ACCEPT_FOR_FURTHER_PAPER_REVIEW_ONLY",
        )
        required_action = "OPERATOR_DECISION_REQUIRED"

    return OperatorReviewPacket(
        schema_version="paper_validation_operator_review_v1",
        run_id=result_packet.run_id,
        correlation_id=result_packet.correlation_id,
        validation_status=result_packet.status,
        recommendation=result_packet.recommendation,
        result_packet=result_packet,
        permitted_operator_actions=actions,
        required_action=required_action,
    )
