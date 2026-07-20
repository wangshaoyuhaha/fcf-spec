from __future__ import annotations

from apps.fcp_0013_candidate_data_evidence_bundle_reconciliation_app_1 import (
    CandidateEvidenceReconciliationPacket,
)

from .contracts import (
    PRIORITY_ORDER,
    CandidateEvidenceGapRemediationPlan,
    EvidenceGapRemediationRequirement,
)


GOVERNANCE_CATEGORIES = frozenset(
    {
        "commercial-entitlement",
        "permitted-use",
        "provider-selection-evidence",
        "retention",
        "retention-rights",
        "rights",
    }
)
QUALITY_CATEGORIES = frozenset({"freshness-latency", "lineage", "schema", "timestamp-revision"})


def _category_requirement(category: str) -> EvidenceGapRemediationRequirement:
    if category in GOVERNANCE_CATEGORIES:
        priority, blocker = "P0", "GOVERNANCE"
        criterion = "REGISTERED_DOCUMENTARY_EVIDENCE_REQUIRED"
    elif category == "cost-quota":
        priority, blocker = "P2", "COST"
        criterion = "REGISTERED_COST_AND_QUOTA_EVIDENCE_REQUIRED"
    elif category == "realtime-coverage":
        priority, blocker = "P1", "COVERAGE"
        criterion = "REGISTERED_REALTIME_COVERAGE_EVIDENCE_REQUIRED"
    elif category in QUALITY_CATEGORIES:
        priority, blocker = "P1", "QUALITY"
        criterion = "REGISTERED_QUALITY_EVIDENCE_REQUIRED"
    else:
        raise ValueError("unregistered evidence category")
    dependencies = ()
    if category == "provider-selection-evidence":
        dependencies = tuple(
            sorted(
                f"gap-{value}"
                for value in GOVERNANCE_CATEGORIES
                if value != "provider-selection-evidence"
            )
        )
    return EvidenceGapRemediationRequirement(
        requirement_id=f"gap-{category}",
        category=category,
        priority=priority,
        blocker_kind=blocker,
        acceptance_criteria=(criterion,),
        dependency_ids=dependencies,
    )


def _field_requirement(kind: str, fields: tuple[str, ...]) -> EvidenceGapRemediationRequirement:
    normalized_kind = kind.lower().replace("_", "-")
    return EvidenceGapRemediationRequirement(
        requirement_id=f"fields-{normalized_kind}",
        category=f"{normalized_kind}-canonical-fields",
        priority="P1",
        blocker_kind="COVERAGE",
        acceptance_criteria=(f"REGISTERED_{kind}_SCHEMA_EVIDENCE_REQUIRED",),
        required_fields=fields,
    )


def build_candidate_evidence_gap_remediation_plan(
    packet: CandidateEvidenceReconciliationPacket,
) -> CandidateEvidenceGapRemediationPlan:
    if not isinstance(packet, CandidateEvidenceReconciliationPacket):
        raise TypeError("packet must be CandidateEvidenceReconciliationPacket")
    if (
        packet.readiness_delta != "EVIDENCE_EXPANDED_NOT_READY"
        or packet.external_activation_state != "BLOCKED"
        or packet.provider_selection_state != "UNSELECTED"
        or packet.network_state != "DISABLED"
    ):
        raise ValueError("source packet boundary is incompatible")
    requirements = [
        _category_requirement(category)
        for category in packet.missing_evidence_categories
    ]
    requirements.extend(
        _field_requirement(kind, tuple(fields))
        for kind, fields in packet.missing_fields_by_kind.items()
    )
    ordered = tuple(
        sorted(
            requirements,
            key=lambda item: (PRIORITY_ORDER[item.priority], item.requirement_id),
        )
    )
    return CandidateEvidenceGapRemediationPlan(
        candidate_id=packet.candidate_id,
        source_packet_sha256=packet.packet_sha256,
        requirements=ordered,
    )
