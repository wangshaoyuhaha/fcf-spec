from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from apps.v2_r2_historical_factor_baseline_app_1.contracts import (
    decimal_value,
    identifier,
    instant,
    utc,
)


_TASK_KINDS = {"EXPLAIN", "CHALLENGE", "EXPLAIN_AND_CHALLENGE"}
_STANCES = {"SUPPORT", "CONTRADICT", "UNCERTAIN", "ABSTAIN"}


def _sha256(value: object, name: str) -> str:
    normalized = str(value).strip()
    if len(normalized) != 64 or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        raise ValueError(f"{name} must be lowercase SHA-256")
    return normalized


@dataclass(frozen=True)
class CognitiveTaskPolicy:
    policy_id: str
    policy_version: str
    minimum_advisory_confidence: Decimal
    max_task_seconds: int
    fallback: str = "SKIP_EXPLANATION"
    target_label: str = "NONE"
    operator_registered: bool = True
    model_invocation_allowed: bool = False
    prompt_execution_allowed: bool = False
    automatic_routing_allowed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "policy_id", identifier(self.policy_id, "policy_id"))
        object.__setattr__(
            self, "policy_version", identifier(self.policy_version, "policy_version")
        )
        confidence = decimal_value(
            self.minimum_advisory_confidence, "minimum_advisory_confidence"
        )
        object.__setattr__(self, "minimum_advisory_confidence", confidence)
        if confidence < 0 or confidence > 1:
            raise ValueError("minimum advisory confidence must be between zero and one")
        if isinstance(self.max_task_seconds, bool) or not 1 <= self.max_task_seconds <= 3600:
            raise ValueError("max_task_seconds must be between 1 and 3600")
        if self.fallback != "SKIP_EXPLANATION" or self.target_label != "NONE":
            raise ValueError("V2-R5 fallback and target label are fixed")
        if self.operator_registered is not True:
            raise ValueError("cognitive task policy requires Operator registration")
        if (
            self.model_invocation_allowed
            or self.prompt_execution_allowed
            or self.automatic_routing_allowed
        ):
            raise ValueError("V2-R5 cannot invoke or route AI")


@dataclass(frozen=True)
class CognitiveTask:
    task_id: str
    correlation_id: str
    anomaly_evidence_hash: str
    requested_at_utc: str
    deadline_at_utc: str
    task_kind: str
    policy_id: str
    policy_version: str
    registered_local_only: bool = True

    def __post_init__(self) -> None:
        for field_name in ("task_id", "correlation_id", "policy_id", "policy_version"):
            object.__setattr__(
                self, field_name, identifier(getattr(self, field_name), field_name)
            )
        object.__setattr__(
            self,
            "anomaly_evidence_hash",
            _sha256(self.anomaly_evidence_hash, "anomaly_evidence_hash"),
        )
        object.__setattr__(
            self, "requested_at_utc", utc(self.requested_at_utc, "requested_at_utc")
        )
        object.__setattr__(
            self, "deadline_at_utc", utc(self.deadline_at_utc, "deadline_at_utc")
        )
        if instant(self.deadline_at_utc) <= instant(self.requested_at_utc):
            raise ValueError("task deadline must follow request time")
        normalized_kind = str(self.task_kind).strip().upper()
        if normalized_kind not in _TASK_KINDS:
            raise ValueError("invalid cognitive task kind")
        object.__setattr__(self, "task_kind", normalized_kind)
        if self.registered_local_only is not True:
            raise ValueError("cognitive task must remain registered and local")


@dataclass(frozen=True)
class RegisteredAdvisoryArtifact:
    artifact_id: str
    artifact_version: str
    task_id: str
    anomaly_evidence_hash: str
    produced_at_utc: str
    stance: str
    confidence: Decimal
    content_sha256: str
    reason_codes: tuple[str, ...]
    source_class: str = "REGISTERED_LOCAL_ARTIFACT"
    value_class: str = "INFERRED"
    operator_registered: bool = True

    def __post_init__(self) -> None:
        for field_name in ("artifact_id", "artifact_version", "task_id"):
            object.__setattr__(
                self, field_name, identifier(getattr(self, field_name), field_name)
            )
        object.__setattr__(
            self,
            "anomaly_evidence_hash",
            _sha256(self.anomaly_evidence_hash, "anomaly_evidence_hash"),
        )
        object.__setattr__(
            self, "produced_at_utc", utc(self.produced_at_utc, "produced_at_utc")
        )
        normalized_stance = str(self.stance).strip().upper()
        if normalized_stance not in _STANCES:
            raise ValueError("invalid advisory stance")
        object.__setattr__(self, "stance", normalized_stance)
        confidence = decimal_value(self.confidence, "confidence")
        object.__setattr__(self, "confidence", confidence)
        if confidence < 0 or confidence > 1:
            raise ValueError("advisory confidence must be between zero and one")
        object.__setattr__(
            self, "content_sha256", _sha256(self.content_sha256, "content_sha256")
        )
        reasons = tuple(identifier(reason, "reason_code") for reason in self.reason_codes)
        if len(reasons) > 20 or len(set(reasons)) != len(reasons):
            raise ValueError("advisory reason codes must be unique and bounded")
        object.__setattr__(self, "reason_codes", reasons)
        if self.source_class != "REGISTERED_LOCAL_ARTIFACT" or self.value_class != "INFERRED":
            raise ValueError("advisory source and value class exceed V2-R5 scope")
        if self.operator_registered is not True:
            raise ValueError("advisory artifact requires Operator registration")
