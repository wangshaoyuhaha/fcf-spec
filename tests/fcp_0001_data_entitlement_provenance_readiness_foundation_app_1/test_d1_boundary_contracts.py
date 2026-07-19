from types import MappingProxyType

import pytest

from apps.fcp_0001_data_entitlement_provenance_readiness_foundation_app_1 import (
    FCP_0001_DATA_ENTITLEMENT_PROVENANCE_BOUNDARY,
    DataEntitlementProvenanceBoundary,
    EntitlementEvidenceState,
    EntitlementReviewRequest,
    ExpiryKind,
    FindingSeverity,
    ReadinessFinding,
    RevocationState,
    SourceEntitlementRecord,
)


def _registered_record() -> SourceEntitlementRecord:
    return SourceEntitlementRecord(
        record_id="entitlement-record-1",
        record_version="v1",
        source_id="registered-source-1",
        evidence_state=EntitlementEvidenceState.REGISTERED,
        market_scope_ids=("a-share",),
        field_ids=("close", "open", "close"),
        permitted_use_ids=("local-research",),
        rights_evidence_ids=("rights-evidence-1",),
        lineage_evidence_ids=("lineage-evidence-1",),
        retention_days=30,
        freshness_objective_seconds=60,
        latency_objective_ms=500,
        monthly_cost_minor_units=0,
        currency_code="cny",
        expiry_kind=ExpiryKind.PERPETUAL,
        revocation_state=RevocationState.ACTIVE,
        evidence_ids=("registered-evidence-1",),
    )


def test_boundary_is_fail_closed() -> None:
    boundary = FCP_0001_DATA_ENTITLEMENT_PROVENANCE_BOUNDARY
    assert boundary.paper_only is True
    assert boundary.local_only is True
    assert boundary.loopback_only is True
    assert boundary.sidecar_only is True
    assert boundary.registered_artifact_only is True
    assert boundary.read_only is True
    assert boundary.operator_review_required is True
    assert boundary.deterministic_authority_preserved is True
    assert boundary.registered_evidence_authority_preserved is True
    assert boundary.ai_advisory_only is True
    assert boundary.network_retrieval_allowed is False
    assert boundary.credential_material_allowed is False
    assert boundary.live_vendor_connection_allowed is False
    assert boundary.market_or_vendor_selection_allowed is False
    assert boundary.license_approval_allowed is False
    assert boundary.phase_authorization_allowed is False
    assert boundary.gap_closure_allowed is False
    assert boundary.automatic_activation_allowed is False
    assert boundary.broker_connection_allowed is False
    assert boundary.exchange_connection_allowed is False
    assert boundary.account_access_allowed is False
    assert boundary.balance_access_allowed is False
    assert boundary.position_access_allowed is False
    assert boundary.wallet_access_allowed is False
    assert boundary.order_path_allowed is False
    assert boundary.real_execution_allowed is False


def test_boundary_rejects_capability_widening() -> None:
    with pytest.raises(ValueError, match="prohibited entitlement readiness"):
        DataEntitlementProvenanceBoundary(network_retrieval_allowed=True)


def test_review_request_is_loopback_and_deterministic() -> None:
    request = EntitlementReviewRequest(
        request_id="request-1",
        correlation_id="correlation-1",
        source_id="registered-source-1",
        evaluated_at_utc="2026-07-19T10:00:00Z",
        intended_use_id="local-research",
        required_field_ids=("open", "close", "open"),
    )
    assert request.required_field_ids == ("close", "open")
    with pytest.raises(ValueError, match="exactly 127.0.0.1"):
        EntitlementReviewRequest(
            request_id="request-2",
            correlation_id="correlation-2",
            source_id="registered-source-1",
            evaluated_at_utc="2026-07-19T10:00:00Z",
            intended_use_id="local-research",
            required_field_ids=("close",),
            peer_host="localhost",
        )


def test_registered_record_is_immutable_and_complete() -> None:
    record = _registered_record()
    assert record.field_ids == ("close", "open")
    assert record.currency_code == "CNY"
    payload = record.as_payload()
    assert isinstance(payload, MappingProxyType)
    assert payload["phase_authorization_allowed"] is False
    with pytest.raises(TypeError):
        payload["source_id"] = "changed"  # type: ignore[index]


def test_unregistered_record_cannot_assert_evidence() -> None:
    with pytest.raises(ValueError, match="cannot assert evidence"):
        SourceEntitlementRecord(
            record_id="entitlement-record-2",
            record_version="v1",
            source_id="registered-source-2",
            evidence_state=EntitlementEvidenceState.NOT_RESEARCHED,
            evidence_ids=("unsupported-evidence",),
        )


def test_expiry_and_cost_contracts_fail_closed() -> None:
    with pytest.raises(ValueError, match="require expires_at_utc"):
        SourceEntitlementRecord(
            record_id="entitlement-record-3",
            record_version="v1",
            source_id="registered-source-3",
            evidence_state=EntitlementEvidenceState.REGISTERED,
            expiry_kind=ExpiryKind.DATE_BOUND,
            evidence_ids=("registered-evidence-3",),
        )
    with pytest.raises(ValueError, match="currency_code requires"):
        SourceEntitlementRecord(
            record_id="entitlement-record-4",
            record_version="v1",
            source_id="registered-source-4",
            evidence_state=EntitlementEvidenceState.REGISTERED,
            currency_code="CNY",
            evidence_ids=("registered-evidence-4",),
        )


def test_readiness_finding_is_immutable_and_normalized() -> None:
    finding = ReadinessFinding(
        code="rights-evidence-missing",
        severity=FindingSeverity.BLOCKING,
        evidence_ids=("evidence-2", "evidence-1", "evidence-2"),
    )
    assert finding.evidence_ids == ("evidence-1", "evidence-2")
    assert isinstance(finding.as_payload(), MappingProxyType)
