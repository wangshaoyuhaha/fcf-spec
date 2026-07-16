from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .artifact_reader import LocalRegisteredArtifactReader
from .contracts import GatewayReadReceipt, GatewayReadRequest, RegisteredArtifactSource
from .normalization import NormalizedArtifactEnvelope, normalize_verified_artifact
from .registry import RegisteredArtifactRegistry


class SourcePolicyStatus(str, Enum):
    READY_FOR_OPERATOR_REVIEW = "READY_FOR_OPERATOR_REVIEW"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class SourcePolicyDecision:
    source_id: str
    evidence_id: str
    status: SourcePolicyStatus
    blocking_reasons: tuple[str, ...] = ()
    degradation_reasons: tuple[str, ...] = ()
    operator_review_required: bool = True
    automatic_activation_allowed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", SourcePolicyStatus(self.status))
        for field in ("blocking_reasons", "degradation_reasons"):
            value = tuple(sorted(set(getattr(self, field))))
            object.__setattr__(self, field, value)
        if self.operator_review_required is not True:
            raise ValueError("operator_review_required must be true")
        if self.automatic_activation_allowed is not False:
            raise ValueError("automatic_activation_allowed must be false")
        if self.status is SourcePolicyStatus.BLOCKED and not self.blocking_reasons:
            raise ValueError("blocked policy decision requires a reason")
        if self.status is not SourcePolicyStatus.BLOCKED and self.blocking_reasons:
            raise ValueError("non-blocked policy decision cannot include blocking reasons")
        if self.status is SourcePolicyStatus.READY_FOR_OPERATOR_REVIEW and self.degradation_reasons:
            raise ValueError("ready policy decision cannot include degradation reasons")


def evaluate_source_policy(source: RegisteredArtifactSource) -> SourcePolicyDecision:
    if not isinstance(source, RegisteredArtifactSource):
        raise TypeError("source must be a RegisteredArtifactSource")
    blocked: list[str] = []
    degraded: list[str] = []
    if source.allowed_use == "PROHIBITED":
        blocked.append("source-use-prohibited")
    if source.license_type == "RESTRICTED":
        blocked.append("source-license-restricted")
    if source.allowed_use == "RESTRICTED":
        degraded.append("source-use-restricted")
    if source.license_type == "UNKNOWN":
        degraded.append("source-license-unknown")
    if source.freshness_status in {"AGING", "STALE", "UNKNOWN"}:
        degraded.append(f"source-freshness-{source.freshness_status.lower()}")
    if source.trust_level in {"LOW", "UNKNOWN"}:
        degraded.append(f"source-trust-{source.trust_level.lower()}")
    if source.source_class == "UNKNOWN":
        degraded.append("source-class-unknown")
    if blocked:
        status = SourcePolicyStatus.BLOCKED
    elif degraded:
        status = SourcePolicyStatus.DEGRADED
    else:
        status = SourcePolicyStatus.READY_FOR_OPERATOR_REVIEW
    return SourcePolicyDecision(
        source_id=source.source_id,
        evidence_id=source.evidence_id,
        status=status,
        blocking_reasons=tuple(blocked),
        degradation_reasons=tuple(degraded),
    )


@dataclass(frozen=True)
class GatewayQueryOutcome:
    request: GatewayReadRequest
    policy_decision: SourcePolicyDecision
    receipt: GatewayReadReceipt | None
    envelope: NormalizedArtifactEnvelope | None

    def __post_init__(self) -> None:
        blocked = self.policy_decision.status is SourcePolicyStatus.BLOCKED
        if blocked and (self.receipt is not None or self.envelope is not None):
            raise ValueError("blocked query outcome must not expose artifact data")
        if not blocked and (self.receipt is None or self.envelope is None):
            raise ValueError("accepted query outcome requires receipt and envelope")
        if self.request.source_id != self.policy_decision.source_id:
            raise ValueError("query source linkage mismatch")


class ReadOnlyDataGatewayService:
    def __init__(
        self,
        registry: RegisteredArtifactRegistry,
        reader: LocalRegisteredArtifactReader,
    ) -> None:
        if not isinstance(registry, RegisteredArtifactRegistry):
            raise TypeError("registry must be a RegisteredArtifactRegistry")
        if not isinstance(reader, LocalRegisteredArtifactReader):
            raise TypeError("reader must be a LocalRegisteredArtifactReader")
        self._registry = registry
        self._reader = reader

    def query(self, request: GatewayReadRequest) -> GatewayQueryOutcome:
        source = self._registry.require(request.source_id)
        decision = evaluate_source_policy(source)
        if decision.status is SourcePolicyStatus.BLOCKED:
            return GatewayQueryOutcome(request, decision, None, None)
        verified = self._reader.read(request, self._registry)
        envelope = normalize_verified_artifact(verified)
        return GatewayQueryOutcome(request, decision, verified.receipt, envelope)
