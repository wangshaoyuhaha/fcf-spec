from __future__ import annotations

from dataclasses import dataclass

from .boundary import READ_ONLY_DATA_GATEWAY_BOUNDARY
from .presentation import GatewayOperatorReviewPacket, GatewayPresentationModel


@dataclass(frozen=True)
class GatewayRuntimeAcceptance:
    status: str
    registry_sha256: str
    registered_source_count: int
    ready_count: int
    degraded_count: int
    blocked_count: int
    paper_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    registered_artifact_only: bool = True
    operator_review_required: bool = True
    deterministic_authority_preserved: bool = True
    registered_evidence_authority_preserved: bool = True
    automatic_activation_allowed: bool = False
    trading_or_execution_path_allowed: bool = False

    def __post_init__(self) -> None:
        if self.status != "READY_FOR_OPERATOR_ACCEPTANCE":
            raise ValueError("gateway acceptance status is invalid")
        required=(self.paper_only,self.local_only,self.loopback_only,
            self.registered_artifact_only,self.operator_review_required,
            self.deterministic_authority_preserved,
            self.registered_evidence_authority_preserved)
        if not all(required) or self.automatic_activation_allowed or self.trading_or_execution_path_allowed:
            raise ValueError("gateway acceptance boundary is invalid")
        if self.registered_source_count <= 0:
            raise ValueError("gateway acceptance requires registered sources")
        if self.ready_count+self.degraded_count+self.blocked_count != self.registered_source_count:
            raise ValueError("gateway acceptance counts do not reconcile")


def build_gateway_runtime_acceptance(
    model: GatewayPresentationModel,
    packet: GatewayOperatorReviewPacket,
) -> GatewayRuntimeAcceptance:
    if model.registry_sha256 != packet.registry_sha256:
        raise ValueError("presentation and review packet registry mismatch")
    if tuple(item.source_id for item in model.sources) != packet.source_ids:
        raise ValueError("presentation and review packet source mismatch")
    boundary=READ_ONLY_DATA_GATEWAY_BOUNDARY
    return GatewayRuntimeAcceptance(
        status="READY_FOR_OPERATOR_ACCEPTANCE",
        registry_sha256=model.registry_sha256,
        registered_source_count=len(model.sources),
        ready_count=packet.ready_count,
        degraded_count=packet.degraded_count,
        blocked_count=packet.blocked_count,
        paper_only=boundary.paper_only,
        local_only=boundary.local_only,
        loopback_only=boundary.loopback_only,
        registered_artifact_only=boundary.registered_artifact_only,
        operator_review_required=boundary.operator_review_required,
        deterministic_authority_preserved=boundary.deterministic_authority_preserved,
        registered_evidence_authority_preserved=boundary.registered_evidence_authority_preserved,
    )
