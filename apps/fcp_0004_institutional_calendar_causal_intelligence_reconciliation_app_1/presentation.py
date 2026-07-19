from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .boundary import FCP_0004_BOUNDARY
from .contracts import InstitutionalArchitectureReconciliation


@dataclass(frozen=True)
class InstitutionalArchitectureReconciliationPacket:
    payload: Mapping[str, object]
    operator_review_required: bool = True
    read_only: bool = True
    phase_authorization_allowed: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.payload, MappingProxyType):
            raise TypeError("architecture reconciliation packet must be immutable")
        if not self.operator_review_required or not self.read_only:
            raise ValueError("architecture reconciliation packet must remain read-only")
        if self.phase_authorization_allowed:
            raise ValueError("architecture reconciliation cannot authorize a phase")


def build_institutional_architecture_reconciliation_packet(
    result: InstitutionalArchitectureReconciliation,
) -> InstitutionalArchitectureReconciliationPacket:
    coverage_rows = tuple(
        MappingProxyType({"gap_id": gap_id, "stage_ids": stage_ids})
        for gap_id, stage_ids in result.gap_coverage
    )
    finding_rows = tuple(
        MappingProxyType(
            {
                "code": item.code,
                "severity": item.severity,
                "subject_ids": item.subject_ids,
            }
        )
        for item in result.findings
    )
    return InstitutionalArchitectureReconciliationPacket(
        MappingProxyType(
            {
                "automatic_scoring_allowed": False,
                "automatic_weight_change_allowed": False,
                "expected_overlap_gap_ids": result.expected_overlap_gap_ids,
                "factor_activation_claimed": False,
                "findings": finding_rows,
                "gap_coverage": coverage_rows,
                "network_allowed": False,
                "operator_decision": "ACCEPTED_ARCHITECTURE",
                "operator_review_required": True,
                "phase_authorization_allowed": False,
                "production_gap_closure_claimed": False,
                "proposal_id": "FCF-FCP-0004",
                "proposal_status": "ACCEPTED_ARCHITECTURE",
                "read_only": True,
                "reconciliation_hash": result.reconciliation_hash,
                "registry_hash": result.registry_hash,
                "state": result.state,
            }
        )
    )


def validate_institutional_architecture_reconciliation_acceptance(
    packet: InstitutionalArchitectureReconciliationPacket,
) -> Mapping[str, bool]:
    checks = MappingProxyType(
        {
            "accepted_architecture_preserved": packet.payload["proposal_status"]
            == "ACCEPTED_ARCHITECTURE",
            "deterministic_authority_preserved": FCP_0004_BOUNDARY.deterministic_authority_preserved,
            "evidence_authority_preserved": FCP_0004_BOUNDARY.registered_evidence_authority_preserved,
            "factor_activation_denied": packet.payload["factor_activation_claimed"]
            is False,
            "network_denied": packet.payload["network_allowed"] is False,
            "operator_review_required": packet.payload["operator_review_required"]
            is True,
            "phase_denied": packet.payload["phase_authorization_allowed"] is False,
            "production_gap_closure_denied": packet.payload[
                "production_gap_closure_claimed"
            ]
            is False,
            "ready_for_review": packet.payload["state"]
            == "READY_FOR_OPERATOR_REVIEW",
            "weight_change_denied": packet.payload[
                "automatic_weight_change_allowed"
            ]
            is False,
        }
    )
    if not all(checks.values()):
        raise ValueError("institutional architecture reconciliation acceptance failed")
    return checks
