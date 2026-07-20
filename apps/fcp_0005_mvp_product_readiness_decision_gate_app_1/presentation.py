from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .boundary import FCP_0005_BOUNDARY
from .contracts import MvpProductReadinessDecision


@dataclass(frozen=True)
class MvpProductReadinessPacket:
    payload: Mapping[str, object]
    read_only: bool = True
    operator_review_required: bool = True
    market_selection_allowed: bool = False
    phase_authorization_allowed: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.payload, MappingProxyType):
            raise TypeError("MVP product readiness packet must be immutable")
        if not self.read_only or not self.operator_review_required:
            raise ValueError("MVP product readiness packet must remain read-only")
        if self.market_selection_allowed or self.phase_authorization_allowed:
            raise ValueError("MVP product readiness packet cannot authorize product state")


def build_mvp_product_readiness_packet(
    decision: MvpProductReadinessDecision,
) -> MvpProductReadinessPacket:
    rows = tuple(
        MappingProxyType(
            {
                "blocked_dimensions": item.blocked_dimensions,
                "candidate_id": item.candidate_id,
                "conflict_dimensions": item.conflict_dimensions,
                "evidence_ids": item.evidence_ids,
                "missing_dimensions": item.missing_dimensions,
                "not_yet_available_dimensions": item.not_yet_available_dimensions,
                "readiness_hash": item.readiness_hash,
                "stale_dimensions": item.stale_dimensions,
                "state": item.state,
            }
        )
        for item in decision.candidate_results
    )
    return MvpProductReadinessPacket(
        MappingProxyType(
            {
                "automatic_ranking_applied": False,
                "candidate_results": rows,
                "decision_hash": decision.decision_hash,
                "market_selection_allowed": False,
                "network_allowed": False,
                "operator_decision": "PENDING",
                "operator_review_required": True,
                "phase_authorization_allowed": False,
                "production_gap_closure_claimed": False,
                "proposal_id": "FCF-FCP-0005",
                "proposal_status": "NEEDS_RESEARCH",
                "read_only": True,
                "ready_candidate_ids": decision.ready_candidate_ids,
                "selected_market_id": None,
                "state": decision.state,
            }
        )
    )


def validate_mvp_product_readiness_acceptance(
    packet: MvpProductReadinessPacket,
) -> Mapping[str, bool]:
    checks = MappingProxyType(
        {
            "automatic_ranking_denied": packet.payload["automatic_ranking_applied"] is False,
            "deterministic_authority_preserved": FCP_0005_BOUNDARY.deterministic_authority_preserved,
            "evidence_authority_preserved": FCP_0005_BOUNDARY.registered_evidence_authority_preserved,
            "market_selection_denied": packet.payload["market_selection_allowed"] is False,
            "network_denied": packet.payload["network_allowed"] is False,
            "operator_review_required": packet.payload["operator_review_required"] is True,
            "phase_denied": packet.payload["phase_authorization_allowed"] is False,
            "production_gap_closure_denied": packet.payload["production_gap_closure_claimed"] is False,
            "proposal_research_only": packet.payload["proposal_status"] == "NEEDS_RESEARCH",
            "selected_market_absent": packet.payload["selected_market_id"] is None,
        }
    )
    if not all(checks.values()):
        raise ValueError("MVP product readiness acceptance failed")
    return checks
