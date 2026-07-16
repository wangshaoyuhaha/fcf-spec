from __future__ import annotations

from dataclasses import dataclass

from .boundary import DATA_AND_CREDENTIAL_GOVERNANCE_BOUNDARY
from .contracts import GovernanceDomain
from .presentation import GovernanceReviewPacket
from .service import GovernanceEvaluationOutcome


@dataclass(frozen=True)
class GovernanceAcceptanceReport:
    status: str
    source_id: str
    overall_status: str
    decision_domains: tuple[str, ...]
    operator_review_required: bool
    read_only: bool
    credential_material_present: bool
    automatic_activation_allowed: bool
    network_retrieval_allowed: bool
    real_execution_allowed: bool


def validate_governance_acceptance(
    outcome: GovernanceEvaluationOutcome,
    packet: GovernanceReviewPacket,
) -> GovernanceAcceptanceReport:
    if not isinstance(outcome, GovernanceEvaluationOutcome):
        raise TypeError("outcome must be a GovernanceEvaluationOutcome")
    if not isinstance(packet, GovernanceReviewPacket):
        raise TypeError("packet must be a GovernanceReviewPacket")
    expected_domains = tuple(sorted(item.value for item in GovernanceDomain))
    actual_domains = tuple(sorted(item.domain.value for item in outcome.audit_record.decisions))
    if actual_domains != expected_domains:
        raise ValueError("acceptance requires all governance domains")
    if packet.payload["source_id"] != outcome.source.source_id:
        raise ValueError("acceptance source linkage mismatch")
    if packet.payload["overall_status"] != outcome.audit_record.overall_status.value:
        raise ValueError("acceptance status linkage mismatch")
    if packet.credential_material_present or packet.automatic_activation_allowed:
        raise ValueError("acceptance packet violates credential or activation boundary")
    boundary = DATA_AND_CREDENTIAL_GOVERNANCE_BOUNDARY
    return GovernanceAcceptanceReport(
        status="PASS",
        source_id=outcome.source.source_id,
        overall_status=outcome.audit_record.overall_status.value,
        decision_domains=actual_domains,
        operator_review_required=packet.operator_review_required,
        read_only=packet.read_only,
        credential_material_present=packet.credential_material_present,
        automatic_activation_allowed=packet.automatic_activation_allowed,
        network_retrieval_allowed=boundary.network_retrieval_allowed,
        real_execution_allowed=boundary.real_execution_allowed,
    )
