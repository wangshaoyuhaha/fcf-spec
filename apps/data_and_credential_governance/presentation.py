from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .service import GovernanceEvaluationOutcome


@dataclass(frozen=True)
class GovernanceReviewPacket:
    payload: Mapping[str, object]
    operator_review_required: bool = True
    read_only: bool = True
    credential_material_present: bool = False
    automatic_activation_allowed: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.payload, MappingProxyType):
            raise TypeError("review packet payload must be immutable")
        if self.operator_review_required is not True or self.read_only is not True:
            raise ValueError("review packet must remain read-only and Operator-reviewable")
        if self.credential_material_present is not False:
            raise ValueError("review packet must not contain credential material")
        if self.automatic_activation_allowed is not False:
            raise ValueError("review packet cannot allow automatic activation")


def build_governance_review_packet(outcome: GovernanceEvaluationOutcome) -> GovernanceReviewPacket:
    if not isinstance(outcome, GovernanceEvaluationOutcome):
        raise TypeError("outcome must be a GovernanceEvaluationOutcome")
    decisions = tuple(
        MappingProxyType({
            "blocking_reasons": item.blocking_reasons,
            "degradation_reasons": item.degradation_reasons,
            "domain": item.domain.value,
            "evidence_ids": item.evidence_ids,
            "policy_id": item.policy.policy_id,
            "policy_version": item.policy.policy_version,
            "status": item.status.value,
        })
        for item in outcome.audit_record.decisions
    )
    payload = MappingProxyType({
        "automatic_activation_allowed": False,
        "correlation_id": outcome.request.correlation_id,
        "credential_material_present": False,
        "decisions": decisions,
        "freshness_band": outcome.freshness_band.value,
        "operator_review_required": True,
        "overall_status": outcome.audit_record.overall_status.value,
        "read_only": True,
        "registry_sha256": MappingProxyType({
            "credential_reference": outcome.credential_reference_registry_sha256,
            "freshness": outcome.freshness_registry_sha256,
            "license": outcome.license_registry_sha256,
        }),
        "request_id": outcome.request.request_id,
        "source_evidence_id": outcome.source.evidence_id,
        "source_id": outcome.source.source_id,
    })
    return GovernanceReviewPacket(payload)
