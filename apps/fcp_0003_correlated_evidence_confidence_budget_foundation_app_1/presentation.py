from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .boundary import FCP_0003_BOUNDARY
from .budget import RegisteredEvidenceDependenceRegistry
from .contracts import ConfidenceBudgetEvaluation


@dataclass(frozen=True)
class ConfidenceBudgetReviewPacket:
    payload: Mapping[str, object]
    operator_review_required: bool = True
    read_only: bool = True
    phase_authorization_allowed: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.payload, MappingProxyType):
            raise TypeError("confidence budget review packet must be immutable")
        if not self.operator_review_required or not self.read_only or self.phase_authorization_allowed:
            raise ValueError("confidence budget review packet boundary violation")


def build_confidence_budget_review_packet(
    registry: RegisteredEvidenceDependenceRegistry,
    evaluation: ConfidenceBudgetEvaluation,
) -> ConfidenceBudgetReviewPacket:
    allocation_rows = tuple(
        MappingProxyType(
            {
                "allocated_confidence_bps": item.allocated_confidence_bps,
                "claim_id": item.claim_id,
                "group_id": item.group_id,
                "requested_confidence_bps": item.requested_confidence_bps,
                "signed_contribution_bps": item.signed_contribution_bps,
                "suppression_reasons": item.suppression_reasons,
            }
        )
        for item in evaluation.allocations
    )
    group_rows = tuple(
        MappingProxyType(
            {
                "allocated_confidence_bps": item.allocated_confidence_bps,
                "claim_ids": item.claim_ids,
                "dependence_type": item.dependence_type,
                "group_cap_bps": item.group_cap_bps,
                "group_id": item.group_id,
                "repeated_confirmation_prevented": item.repeated_confirmation_prevented,
                "requested_usable_bps": item.requested_usable_bps,
            }
        )
        for item in evaluation.group_findings
    )
    return ConfidenceBudgetReviewPacket(
        MappingProxyType(
            {
                "abstention_reasons": evaluation.abstention_reasons,
                "allocations": allocation_rows,
                "automatic_approval_allowed": False,
                "automatic_scoring_allowed": False,
                "automatic_weight_change_allowed": False,
                "evaluation_hash": evaluation.evaluation_hash,
                "gross_allocated_bps": evaluation.gross_allocated_bps,
                "group_findings": group_rows,
                "network_allowed": False,
                "operator_review_required": True,
                "phase_authorization_allowed": False,
                "proposal_id": "FCF-FCP-0003",
                "proposal_status": "NEEDS_RESEARCH",
                "read_only": True,
                "registry_hash": registry.registry_hash,
                "scoring_authority_claimed": False,
                "state": evaluation.state,
            }
        )
    )


def validate_confidence_budget_acceptance(
    packet: ConfidenceBudgetReviewPacket,
) -> Mapping[str, bool]:
    checks = MappingProxyType(
        {
            "deterministic_authority_preserved": FCP_0003_BOUNDARY.deterministic_authority_preserved,
            "evidence_authority_preserved": FCP_0003_BOUNDARY.registered_evidence_authority_preserved,
            "network_denied": packet.payload["network_allowed"] is False,
            "operator_review_required": packet.payload["operator_review_required"] is True,
            "phase_denied": packet.payload["phase_authorization_allowed"] is False,
            "research_only": packet.payload["proposal_status"] == "NEEDS_RESEARCH",
            "scoring_denied": packet.payload["scoring_authority_claimed"] is False,
            "weight_change_denied": packet.payload["automatic_weight_change_allowed"] is False,
        }
    )
    if not all(checks.values()):
        raise ValueError("confidence budget acceptance failed")
    return checks
