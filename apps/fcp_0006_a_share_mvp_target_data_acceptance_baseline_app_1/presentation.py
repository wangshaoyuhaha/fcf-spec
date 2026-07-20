from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .boundary import FCP_0006_BOUNDARY
from .contracts import AShareMvpBaselineRegistry, AShareMvpBaselineResult


@dataclass(frozen=True)
class AShareMvpBaselinePacket:
    payload: Mapping[str, object]
    read_only: bool = True
    operator_review_required: bool = True
    product_market_selection_allowed: bool = False
    phase_authorization_allowed: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.payload, MappingProxyType):
            raise TypeError("A-share MVP baseline packet must be immutable")
        if not self.read_only or not self.operator_review_required:
            raise ValueError("A-share MVP baseline packet must remain read-only")
        if self.product_market_selection_allowed or self.phase_authorization_allowed:
            raise ValueError("A-share MVP baseline packet cannot authorize product state")


def build_a_share_mvp_baseline_packet(
    registry: AShareMvpBaselineRegistry,
    result: AShareMvpBaselineResult,
) -> AShareMvpBaselinePacket:
    target_rows = tuple(
        MappingProxyType(
            {
                "benchmark_id": item.benchmark_id,
                "horizon_id": item.horizon_id,
                "label_maturity_id": item.label_maturity_id,
                "target_family": item.target_family,
                "target_hash": item.target_hash,
                "target_id": item.target_id,
                "universe_policy_id": item.universe_policy_id,
            }
        )
        for item in registry.targets
    )
    data_rows = tuple(
        MappingProxyType(
            {
                "availability_time_required": item.availability_time_required,
                "domain": item.domain,
                "entitlement_approved": item.entitlement_approved,
                "field_id": item.field_id,
                "market_session_version_required": item.market_session_version_required,
                "point_in_time_required": item.point_in_time_required,
                "provider_id": item.provider_id,
                "requirement_hash": item.requirement_hash,
                "requirement_level": item.requirement_level,
                "source_semantics_id": item.source_semantics_id,
            }
        )
        for item in registry.data_requirements
    )
    obligation_rows = tuple(
        MappingProxyType(
            {
                "category": item.category,
                "empirical_threshold": item.empirical_threshold,
                "evidence_artifact_id": item.evidence_artifact_id,
                "evidence_digest": item.evidence_digest,
                "evidence_state": item.evidence_state,
                "metric_id": item.metric_id,
                "obligation_hash": item.obligation_hash,
                "obligation_id": item.obligation_id,
            }
        )
        for item in registry.obligations
    )
    return AShareMvpBaselinePacket(
        MappingProxyType(
            {
                "data_requirements": data_rows,
                "evidence_required_obligation_ids": result.evidence_required_obligation_ids,
                "fcp_0005_readiness_claimed": False,
                "obligations": obligation_rows,
                "operator_decision": registry.operator_decision,
                "operator_review_required": True,
                "phase_authorization_allowed": False,
                "product_market_selection_allowed": False,
                "production_gap_closure_claimed": False,
                "proposal_id": registry.proposal_id,
                "proposal_status": registry.proposal_status,
                "provider_selection_allowed": False,
                "read_only": True,
                "registry_hash": registry.registry_hash,
                "research_priority_market_id": registry.research_priority_market_id,
                "result_hash": result.result_hash,
                "selected_market_id": None,
                "state": result.state,
                "targets": target_rows,
            }
        )
    )


def validate_a_share_mvp_baseline_acceptance(
    packet: AShareMvpBaselinePacket,
) -> Mapping[str, bool]:
    checks = MappingProxyType(
        {
            "a_share_research_priority_explicit": (
                packet.payload["research_priority_market_id"] == "A-SHARE"
            ),
            "data_rights_not_approved": all(
                row["entitlement_approved"] is False
                for row in packet.payload["data_requirements"]
            ),
            "deterministic_authority_preserved": (
                FCP_0006_BOUNDARY.deterministic_authority_preserved
            ),
            "evidence_authority_preserved": (
                FCP_0006_BOUNDARY.registered_evidence_authority_preserved
            ),
            "fcp_0005_readiness_not_claimed": (
                packet.payload["fcp_0005_readiness_claimed"] is False
            ),
            "market_selection_denied": (
                packet.payload["product_market_selection_allowed"] is False
                and packet.payload["selected_market_id"] is None
            ),
            "network_denied": FCP_0006_BOUNDARY.network_allowed is False,
            "operator_review_required": (
                packet.payload["operator_review_required"] is True
            ),
            "phase_denied": packet.payload["phase_authorization_allowed"] is False,
            "production_gap_closure_denied": (
                packet.payload["production_gap_closure_claimed"] is False
            ),
            "provider_selection_denied": (
                packet.payload["provider_selection_allowed"] is False
            ),
            "thresholds_not_claimed": all(
                row["empirical_threshold"] is None
                for row in packet.payload["obligations"]
            ),
        }
    )
    if not all(checks.values()):
        raise ValueError("A-share MVP baseline acceptance failed")
    return checks
