from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .boundary import FCP_0002_BOUNDARY
from .contracts import CounterfactualFinding, ResearchDecisionSnapshot


@dataclass(frozen=True)
class CounterfactualReviewPacket:
    payload: Mapping[str, object]
    operator_review_required: bool = True
    read_only: bool = True
    phase_authorization_allowed: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.payload, MappingProxyType):
            raise TypeError("review packet must be immutable")
        if not self.operator_review_required or not self.read_only or self.phase_authorization_allowed:
            raise ValueError("review packet boundary violation")


def build_counterfactual_review_packet(
    decision: ResearchDecisionSnapshot,
    findings: tuple[CounterfactualFinding, ...],
) -> CounterfactualReviewPacket:
    rows = tuple(MappingProxyType({
        "candidate_id": item.candidate_id,
        "classification": item.classification,
        "disposition": item.disposition,
        "outcome_evidence_hashes": item.outcome_evidence_hashes,
        "post_hoc_contamination": item.post_hoc_contamination,
        "realized_utility_bps": item.realized_utility_bps,
        "selected_delta_bps": item.selected_delta_bps,
    }) for item in findings)
    return CounterfactualReviewPacket(MappingProxyType({
        "automatic_approval_allowed": False,
        "decision_hash": decision.decision_hash,
        "decision_rewrite_allowed": False,
        "findings": rows,
        "network_allowed": False,
        "operator_review_required": True,
        "phase_authorization_allowed": False,
        "proposal_id": "FCF-FCP-0002",
        "proposal_status": "NEEDS_RESEARCH",
        "read_only": True,
    }))


def validate_counterfactual_acceptance(packet: CounterfactualReviewPacket) -> Mapping[str, bool]:
    checks = MappingProxyType({
        "authority_preserved": FCP_0002_BOUNDARY.deterministic_authority_preserved,
        "immutable_decision": packet.payload["decision_rewrite_allowed"] is False,
        "network_denied": packet.payload["network_allowed"] is False,
        "operator_review_required": packet.payload["operator_review_required"] is True,
        "phase_denied": packet.payload["phase_authorization_allowed"] is False,
        "research_only": packet.payload["proposal_status"] == "NEEDS_RESEARCH",
    })
    if not all(checks.values()):
        raise ValueError("counterfactual acceptance failed")
    return checks
