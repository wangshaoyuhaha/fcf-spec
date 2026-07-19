from types import MappingProxyType

import pytest

from apps.fcp_0001_data_entitlement_provenance_readiness_foundation_app_1 import (
    EntitlementEvidenceState,
    EntitlementReviewRequest,
    ExpiryKind,
    ReadinessStatus,
    RevocationState,
    SourceEntitlementRecord,
    SourceEntitlementRegistry,
    build_entitlement_readiness_review_packet,
    evaluate_source_readiness,
)


def _request(source_id: str = "registered-source-1") -> EntitlementReviewRequest:
    return EntitlementReviewRequest(
        request_id="request-1",
        correlation_id="correlation-1",
        source_id=source_id,
        evaluated_at_utc="2026-07-19T10:00:00Z",
        intended_use_id="local-research",
        required_field_ids=("close", "open"),
    )


def _record(
    source_id: str = "registered-source-1",
    *,
    expiry_kind: ExpiryKind = ExpiryKind.PERPETUAL,
    expires_at_utc: str | None = None,
) -> SourceEntitlementRecord:
    return SourceEntitlementRecord(
        record_id=f"record-{source_id}",
        record_version="v1",
        source_id=source_id,
        evidence_state=EntitlementEvidenceState.REGISTERED,
        market_scope_ids=("a-share",),
        field_ids=("open", "close"),
        permitted_use_ids=("local-research",),
        rights_evidence_ids=("rights-evidence-1",),
        lineage_evidence_ids=("lineage-evidence-1",),
        retention_evidence_ids=("retention-evidence-1",),
        service_level_evidence_ids=("service-level-evidence-1",),
        cost_evidence_ids=("cost-evidence-1",),
        expiry_evidence_ids=("expiry-evidence-1",),
        revocation_evidence_ids=("revocation-evidence-1",),
        retention_days=30,
        freshness_objective_seconds=60,
        latency_objective_ms=500,
        monthly_cost_minor_units=0,
        currency_code="CNY",
        expiry_kind=expiry_kind,
        expires_at_utc=expires_at_utc,
        revocation_state=RevocationState.ACTIVE,
        evidence_ids=("registered-evidence-1",),
    )


def test_complete_evidence_is_ready_for_operator_review_only() -> None:
    outcome = evaluate_source_readiness(
        _request(), SourceEntitlementRegistry((_record(),))
    )
    assert outcome.status is ReadinessStatus.READY_FOR_OPERATOR_REVIEW
    assert outcome.proposal_status == "NEEDS_RESEARCH"
    assert outcome.phase_authorization_allowed is False
    assert len(outcome.outcome_sha256) == 64


def test_approaching_expiry_degrades_outcome() -> None:
    record = _record(
        expiry_kind=ExpiryKind.DATE_BOUND,
        expires_at_utc="2026-08-01T10:00:00Z",
    )
    outcome = evaluate_source_readiness(
        _request(), SourceEntitlementRegistry((record,))
    )
    assert outcome.status is ReadinessStatus.DEGRADED


def test_missing_source_blocks_outcome() -> None:
    outcome = evaluate_source_readiness(
        _request("missing-source"), SourceEntitlementRegistry((_record(),))
    )
    assert outcome.status is ReadinessStatus.BLOCKED
    assert "entitlement-record-missing" in {item.code for item in outcome.findings}


def test_outcome_digest_is_deterministic() -> None:
    left = evaluate_source_readiness(
        _request(), SourceEntitlementRegistry((_record(),))
    )
    reordered = SourceEntitlementRecord(
        **{
            **_record().__dict__,
            "field_ids": ("close", "open", "close"),
            "evidence_ids": ("registered-evidence-1", "registered-evidence-1"),
        }
    )
    right = evaluate_source_readiness(
        _request(), SourceEntitlementRegistry((reordered,))
    )
    assert left.outcome_sha256 == right.outcome_sha256


def test_review_packet_is_deeply_read_only_and_fail_closed() -> None:
    outcome = evaluate_source_readiness(
        _request(), SourceEntitlementRegistry((_record(),))
    )
    packet = build_entitlement_readiness_review_packet(outcome)
    assert isinstance(packet.payload, MappingProxyType)
    assert isinstance(packet.payload["record"], MappingProxyType)
    assert isinstance(packet.payload["authority"], MappingProxyType)
    assert isinstance(packet.payload["findings"][0], MappingProxyType)
    assert packet.payload["proposal_status"] == "NEEDS_RESEARCH"
    assert packet.payload["phase_authorization_allowed"] is False
    assert packet.payload["network_retrieval_allowed"] is False
    assert packet.operator_review_required is True
    assert packet.read_only is True
    with pytest.raises(TypeError):
        packet.payload["status"] = "APPROVED"  # type: ignore[index]
