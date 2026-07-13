from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Iterable, Tuple

from .domain import ShadowObservationRequest
from .input_loader import LoadedObservationDataset
from .observation_engine import ShadowObservationPacket


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
    source: str = "deterministic_shadow_runtime"

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "code",
            _require_text(self.code, "code"),
        )
        severity = _require_text(
            self.severity,
            "severity",
        ).upper()
        if severity not in _ALLOWED_SEVERITIES:
            raise ValueError(
                "severity must be LOW, MEDIUM, HIGH, or CRITICAL"
            )
        object.__setattr__(self, "severity", severity)
        object.__setattr__(
            self,
            "message",
            _require_text(self.message, "message"),
        )
        object.__setattr__(
            self,
            "source",
            _require_text(self.source, "source"),
        )

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
                _require_text(
                    getattr(self, field_name),
                    field_name,
                ),
            )

        severity = _require_text(
            self.severity,
            "severity",
        ).upper()
        if severity not in _ALLOWED_SEVERITIES:
            raise ValueError(
                "severity must be LOW, MEDIUM, HIGH, or CRITICAL"
            )
        object.__setattr__(self, "severity", severity)

        evidence = tuple(
            _require_text(item, "evidence_id")
            for item in self.evidence_ids
        )
        if len(set(evidence)) != len(evidence):
            raise ValueError("evidence_ids must be unique")
        object.__setattr__(self, "evidence_ids", evidence)

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
class ShadowObservationResultPacket:
    schema_version: str
    run_id: str
    correlation_id: str
    artifact_id: str
    artifact_version: str
    window_id: str
    policy_id: str
    status: str
    recommendation: str
    observation: ShadowObservationPacket
    risk_flags: Tuple[RiskFlag, ...]
    contradictions: Tuple[ContradictionRecord, ...]
    operator_review_required: bool = True
    paper_only: bool = True
    local_only: bool = True
    passive_observation_only: bool = True
    deterministic_authority: bool = True
    immutable_evidence: bool = True
    automatic_approval_allowed: bool = False
    automatic_promotion_allowed: bool = False
    automatic_baseline_replacement_allowed: bool = False
    automatic_learning_activation_allowed: bool = False
    automatic_archive_allowed: bool = False
    real_execution_allowed: bool = False

    def __post_init__(self) -> None:
        if self.schema_version != "shadow_observation_result_v1":
            raise ValueError("unsupported shadow result schema")
        if self.status not in {
            "BLOCKED",
            "DEGRADED",
            "READY_FOR_OPERATOR_REVIEW",
        }:
            raise ValueError("invalid shadow result status")
        if not self.operator_review_required:
            raise ValueError("operator review must remain required")
        if not (
            self.paper_only
            and self.local_only
            and self.passive_observation_only
            and self.deterministic_authority
            and self.immutable_evidence
        ):
            raise ValueError(
                "shadow result authority boundary was weakened"
            )

        prohibited = (
            self.automatic_approval_allowed,
            self.automatic_promotion_allowed,
            self.automatic_baseline_replacement_allowed,
            self.automatic_learning_activation_allowed,
            self.automatic_archive_allowed,
            self.real_execution_allowed,
        )
        if any(prohibited):
            raise ValueError(
                "automatic or real-world authority is prohibited"
            )

        if self.observation.run_id != self.run_id:
            raise ValueError("observation run_id mismatch")
        if self.observation.correlation_id != self.correlation_id:
            raise ValueError("observation correlation_id mismatch")
        if self.observation.artifact_id != self.artifact_id:
            raise ValueError("observation artifact_id mismatch")
        if self.observation.artifact_version != self.artifact_version:
            raise ValueError("observation artifact_version mismatch")
        if self.observation.window_id != self.window_id:
            raise ValueError("observation window_id mismatch")

        for record in self.contradictions:
            if record.correlation_id != self.correlation_id:
                raise ValueError(
                    "contradiction correlation_id mismatch"
                )

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
            "observation": asdict(self.observation),
            "risk_flags": [
                item.as_dict()
                for item in self.risk_flags
            ],
            "contradictions": [
                item.as_dict()
                for item in self.contradictions
            ],
            "operator_review_required": (
                self.operator_review_required
            ),
            "paper_only": self.paper_only,
            "local_only": self.local_only,
            "passive_observation_only": (
                self.passive_observation_only
            ),
            "deterministic_authority": (
                self.deterministic_authority
            ),
            "immutable_evidence": self.immutable_evidence,
            "automatic_approval_allowed": (
                self.automatic_approval_allowed
            ),
            "automatic_promotion_allowed": (
                self.automatic_promotion_allowed
            ),
            "automatic_baseline_replacement_allowed": (
                self.automatic_baseline_replacement_allowed
            ),
            "automatic_learning_activation_allowed": (
                self.automatic_learning_activation_allowed
            ),
            "automatic_archive_allowed": (
                self.automatic_archive_allowed
            ),
            "real_execution_allowed": (
                self.real_execution_allowed
            ),
        }


@dataclass(frozen=True)
class OperatorReviewPacket:
    schema_version: str
    run_id: str
    correlation_id: str
    observation_status: str
    recommendation: str
    result_packet: ShadowObservationResultPacket
    permitted_operator_actions: Tuple[str, ...]
    required_action: str
    operator_review_required: bool = True
    paper_only: bool = True
    passive_observation_only: bool = True
    automatic_decision_allowed: bool = False
    promotion_action_available: bool = False
    baseline_replacement_action_available: bool = False
    learning_activation_action_available: bool = False
    archive_action_available: bool = False
    real_execution_action_available: bool = False

    def __post_init__(self) -> None:
        if (
            self.schema_version
            != "shadow_observation_operator_review_v1"
        ):
            raise ValueError("unsupported operator review schema")
        if not (
            self.operator_review_required
            and self.paper_only
            and self.passive_observation_only
        ):
            raise ValueError(
                "review packet must remain passive and review-gated"
            )

        prohibited = (
            self.automatic_decision_allowed,
            self.promotion_action_available,
            self.baseline_replacement_action_available,
            self.learning_activation_action_available,
            self.archive_action_available,
            self.real_execution_action_available,
        )
        if any(prohibited):
            raise ValueError(
                "prohibited review action cannot be enabled"
            )

        if self.result_packet.run_id != self.run_id:
            raise ValueError("result packet run_id mismatch")
        if self.result_packet.correlation_id != self.correlation_id:
            raise ValueError(
                "result packet correlation_id mismatch"
            )
        if self.result_packet.status != self.observation_status:
            raise ValueError("result packet status mismatch")
        if not self.permitted_operator_actions:
            raise ValueError(
                "permitted_operator_actions must not be empty"
            )

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "correlation_id": self.correlation_id,
            "observation_status": self.observation_status,
            "recommendation": self.recommendation,
            "result_packet": self.result_packet.as_dict(),
            "permitted_operator_actions": list(
                self.permitted_operator_actions
            ),
            "required_action": self.required_action,
            "operator_review_required": (
                self.operator_review_required
            ),
            "paper_only": self.paper_only,
            "passive_observation_only": (
                self.passive_observation_only
            ),
            "automatic_decision_allowed": (
                self.automatic_decision_allowed
            ),
            "promotion_action_available": (
                self.promotion_action_available
            ),
            "baseline_replacement_action_available": (
                self.baseline_replacement_action_available
            ),
            "learning_activation_action_available": (
                self.learning_activation_action_available
            ),
            "archive_action_available": (
                self.archive_action_available
            ),
            "real_execution_action_available": (
                self.real_execution_action_available
            ),
        }


def _deduplicate_risk_flags(
    flags: Iterable[RiskFlag],
) -> Tuple[RiskFlag, ...]:
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
            seen.add(identity)
            result.append(flag)

    return tuple(result)


def _deduplicate_contradictions(
    records: Iterable[ContradictionRecord],
) -> Tuple[ContradictionRecord, ...]:
    result: list[ContradictionRecord] = []
    seen: set[str] = set()

    for record in records:
        if record.contradiction_id not in seen:
            seen.add(record.contradiction_id)
            result.append(record)

    return tuple(result)


def derive_observation_risk_flags(
    observation: ShadowObservationPacket,
) -> Tuple[RiskFlag, ...]:
    flags: list[RiskFlag] = []

    for reason in observation.blockers:
        flags.append(
            RiskFlag(
                code=reason,
                severity="HIGH",
                message=(
                    "Blocking shadow observation condition: "
                    f"{reason}"
                ),
                blocking=True,
            )
        )

    for reason in observation.warnings:
        flags.append(
            RiskFlag(
                code=reason,
                severity="MEDIUM",
                message=(
                    "Shadow observation review condition: "
                    f"{reason}"
                ),
                blocking=False,
            )
        )

    for code in observation.risk_flags:
        flags.append(
            RiskFlag(
                code=f"registered_risk:{code}",
                severity="MEDIUM",
                message=(
                    "Registered observation risk evidence: "
                    f"{code}"
                ),
                blocking=False,
                source="registered_observation_evidence",
            )
        )

    return tuple(flags)


def derive_observation_contradictions(
    observation: ShadowObservationPacket,
) -> Tuple[ContradictionRecord, ...]:
    return tuple(
        ContradictionRecord(
            contradiction_id=(
                f"registered-observation-{index}"
            ),
            correlation_id=observation.correlation_id,
            category="registered_observation_contradiction",
            statement_a="registered_observation_evidence",
            statement_b=evidence,
            severity="MEDIUM",
            unresolved=True,
            evidence_ids=(evidence,),
        )
        for index, evidence in enumerate(
            observation.contradiction_evidence,
            start=1,
        )
    )


def build_shadow_observation_result_packet(
    *,
    request: ShadowObservationRequest,
    dataset: LoadedObservationDataset,
    observation: ShadowObservationPacket,
    risk_flags: Iterable[RiskFlag] = (),
    contradictions: Iterable[ContradictionRecord] = (),
) -> ShadowObservationResultPacket:
    if dataset.request != request:
        raise ValueError("dataset request mismatch")
    if observation.run_id != request.run_id:
        raise ValueError("observation run_id mismatch")
    if observation.correlation_id != request.correlation_id:
        raise ValueError("observation correlation_id mismatch")

    combined_flags = _deduplicate_risk_flags(
        tuple(derive_observation_risk_flags(observation))
        + tuple(risk_flags)
    )
    combined_contradictions = _deduplicate_contradictions(
        tuple(derive_observation_contradictions(observation))
        + tuple(contradictions)
    )

    blocking_risk = any(
        flag.blocking
        for flag in combined_flags
    )
    blocking_contradiction = any(
        record.unresolved
        and record.severity in {"HIGH", "CRITICAL"}
        for record in combined_contradictions
    )

    if (
        observation.status == "BLOCKED"
        or blocking_risk
        or blocking_contradiction
    ):
        status = "BLOCKED"
        recommendation = "DO_NOT_ADVANCE"
    elif (
        observation.status == "DEGRADED"
        or combined_flags
        or combined_contradictions
    ):
        status = "DEGRADED"
        recommendation = (
            "OPERATOR_REVIEW_DEGRADED_EVIDENCE"
        )
    else:
        status = "READY_FOR_OPERATOR_REVIEW"
        recommendation = (
            "CONTINUE_PASSIVE_OBSERVATION_ONLY_AFTER_OPERATOR_REVIEW"
        )

    return ShadowObservationResultPacket(
        schema_version="shadow_observation_result_v1",
        run_id=request.run_id,
        correlation_id=request.correlation_id,
        artifact_id=request.artifact.artifact_id,
        artifact_version=request.artifact.artifact_version,
        window_id=request.window.window_id,
        policy_id=request.policy.policy_id,
        status=status,
        recommendation=recommendation,
        observation=observation,
        risk_flags=combined_flags,
        contradictions=combined_contradictions,
    )


def build_operator_review_packet(
    result_packet: ShadowObservationResultPacket,
) -> OperatorReviewPacket:
    if result_packet.status == "BLOCKED":
        actions = (
            "ACKNOWLEDGE_BLOCK",
            "REJECT_OBSERVATION",
            "REQUEST_REVISION",
        )
        required_action = (
            "OPERATOR_REVIEW_BLOCKING_EVIDENCE"
        )
    elif result_packet.status == "DEGRADED":
        actions = (
            "ACKNOWLEDGE_DEGRADED_RESULT",
            "REJECT_OBSERVATION",
            "REQUEST_REVISION",
            "CONTINUE_PASSIVE_OBSERVATION_ONLY",
        )
        required_action = (
            "OPERATOR_REVIEW_DEGRADED_EVIDENCE"
        )
    else:
        actions = (
            "ACKNOWLEDGE_RESULT",
            "REJECT_OBSERVATION",
            "REQUEST_REVISION",
            "CONTINUE_PASSIVE_OBSERVATION_ONLY",
        )
        required_action = "OPERATOR_DECISION_REQUIRED"

    return OperatorReviewPacket(
        schema_version="shadow_observation_operator_review_v1",
        run_id=result_packet.run_id,
        correlation_id=result_packet.correlation_id,
        observation_status=result_packet.status,
        recommendation=result_packet.recommendation,
        result_packet=result_packet,
        permitted_operator_actions=actions,
        required_action=required_action,
    )
