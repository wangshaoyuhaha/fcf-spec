from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .boundary import FCP_0001_DATA_ENTITLEMENT_PROVENANCE_BOUNDARY
from .presentation import EntitlementReadinessReviewPacket
from .service import EntitlementReadinessOutcome


_REQUIRED_RECORD_KEYS = frozenset(
    {
        "cost_evidence_ids",
        "evidence_ids",
        "evidence_state",
        "expires_at_utc",
        "expiry_evidence_ids",
        "expiry_kind",
        "field_ids",
        "freshness_objective_seconds",
        "latency_objective_ms",
        "lineage_evidence_ids",
        "market_scope_ids",
        "monthly_cost_minor_units",
        "permitted_use_ids",
        "retention_days",
        "retention_evidence_ids",
        "revocation_evidence_ids",
        "revocation_state",
        "rights_evidence_ids",
        "service_level_evidence_ids",
        "source_id",
    }
)


@dataclass(frozen=True)
class EntitlementReadinessAcceptanceReport:
    status: str
    source_id: str
    readiness_status: str
    checks: Mapping[str, bool]
    operator_review_required: bool = True
    phase_authorization_allowed: bool = False

    def __post_init__(self) -> None:
        if self.status != "PASS":
            raise ValueError("acceptance status must be PASS")
        if not isinstance(self.checks, MappingProxyType):
            raise TypeError("acceptance checks must be immutable")
        if not self.checks or not all(self.checks.values()):
            raise ValueError("acceptance requires every check to pass")
        if self.operator_review_required is not True:
            raise ValueError("operator_review_required must be true")
        if self.phase_authorization_allowed is not False:
            raise ValueError("phase_authorization_allowed must be false")


def validate_entitlement_readiness_acceptance(
    outcome: EntitlementReadinessOutcome,
    packet: EntitlementReadinessReviewPacket,
) -> EntitlementReadinessAcceptanceReport:
    if not isinstance(outcome, EntitlementReadinessOutcome):
        raise TypeError("outcome must be an EntitlementReadinessOutcome")
    if not isinstance(packet, EntitlementReadinessReviewPacket):
        raise TypeError("packet must be an EntitlementReadinessReviewPacket")
    payload = packet.payload
    record_payload = payload.get("record")
    checks = MappingProxyType(
        {
            "authority_preserved": (
                FCP_0001_DATA_ENTITLEMENT_PROVENANCE_BOUNDARY.deterministic_authority_preserved
                and FCP_0001_DATA_ENTITLEMENT_PROVENANCE_BOUNDARY.registered_evidence_authority_preserved
                and FCP_0001_DATA_ENTITLEMENT_PROVENANCE_BOUNDARY.ai_advisory_only
            ),
            "digest_linked": payload.get("outcome_sha256")
            == outcome.outcome_sha256,
            "findings_linked": tuple(
                item["code"] for item in payload.get("findings", ())
            )
            == tuple(item.code for item in outcome.findings),
            "network_denied": (
                packet.network_retrieval_allowed is False
                and payload.get("network_retrieval_allowed") is False
            ),
            "operator_review_required": (
                packet.operator_review_required is True
                and payload.get("operator_review_required") is True
            ),
            "phase_authorization_denied": (
                packet.phase_authorization_allowed is False
                and payload.get("phase_authorization_allowed") is False
            ),
            "proposal_still_needs_research": (
                payload.get("proposal_id") == "FCF-FCP-0001"
                and payload.get("proposal_status") == "NEEDS_RESEARCH"
            ),
            "read_only_registered_artifact": (
                packet.read_only is True
                and packet.registered_artifact_only is True
                and payload.get("read_only") is True
                and payload.get("registered_artifact_only") is True
            ),
            "record_dimensions_complete": (
                isinstance(record_payload, MappingProxyType)
                and _REQUIRED_RECORD_KEYS.issubset(record_payload)
            ),
            "source_linked": payload.get("source_id") == outcome.request.source_id,
            "status_linked": payload.get("status") == outcome.status.value,
        }
    )
    if not all(checks.values()):
        failed = tuple(sorted(key for key, passed in checks.items() if not passed))
        raise ValueError(f"entitlement readiness acceptance failed: {failed}")
    return EntitlementReadinessAcceptanceReport(
        status="PASS",
        source_id=outcome.request.source_id,
        readiness_status=outcome.status.value,
        checks=checks,
    )
