from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .boundary import FCP_0001_DATA_ENTITLEMENT_PROVENANCE_BOUNDARY
from .service import EntitlementReadinessOutcome


@dataclass(frozen=True)
class EntitlementReadinessReviewPacket:
    payload: Mapping[str, object]
    operator_review_required: bool = True
    read_only: bool = True
    registered_artifact_only: bool = True
    network_retrieval_allowed: bool = False
    credential_material_present: bool = False
    phase_authorization_allowed: bool = False
    automatic_activation_allowed: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.payload, MappingProxyType):
            raise TypeError("review packet payload must be immutable")
        required = (
            self.operator_review_required,
            self.read_only,
            self.registered_artifact_only,
        )
        if not all(required):
            raise ValueError("review packet authority flags must remain enabled")
        prohibited = (
            self.network_retrieval_allowed,
            self.credential_material_present,
            self.phase_authorization_allowed,
            self.automatic_activation_allowed,
        )
        if any(prohibited):
            raise ValueError("review packet cannot enable a prohibited capability")


def build_entitlement_readiness_review_packet(
    outcome: EntitlementReadinessOutcome,
) -> EntitlementReadinessReviewPacket:
    if not isinstance(outcome, EntitlementReadinessOutcome):
        raise TypeError("outcome must be an EntitlementReadinessOutcome")
    boundary = FCP_0001_DATA_ENTITLEMENT_PROVENANCE_BOUNDARY
    findings = tuple(
        MappingProxyType(dict(item.as_payload())) for item in outcome.findings
    )
    payload = MappingProxyType(
        {
            "authority": MappingProxyType(
                {
                    "ai_advisory_only": boundary.ai_advisory_only,
                    "deterministic_authority_preserved": (
                        boundary.deterministic_authority_preserved
                    ),
                    "registered_evidence_authority_preserved": (
                        boundary.registered_evidence_authority_preserved
                    ),
                }
            ),
            "correlation_id": outcome.request.correlation_id,
            "credential_material_present": False,
            "findings": findings,
            "network_retrieval_allowed": False,
            "operator_review_required": True,
            "outcome_sha256": outcome.outcome_sha256,
            "phase_authorization_allowed": False,
            "proposal_id": outcome.proposal_id,
            "proposal_status": outcome.proposal_status,
            "read_only": True,
            "record": MappingProxyType(dict(outcome.record.as_payload())),
            "registered_artifact_only": True,
            "registry_sha256": outcome.registry_sha256,
            "request_id": outcome.request.request_id,
            "source_id": outcome.request.source_id,
            "status": outcome.status.value,
        }
    )
    return EntitlementReadinessReviewPacket(payload)
