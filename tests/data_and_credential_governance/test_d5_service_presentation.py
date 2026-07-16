import pytest

from apps.data_and_credential_governance import (
    CredentialReferenceMetadata,
    CredentialReferenceRegistry,
    CredentialReferenceStatus,
    FreshnessPolicy,
    FreshnessPolicyRegistry,
    GovernanceDecisionStatus,
    GovernanceRequest,
    LicensePolicy,
    LicensePolicyRegistry,
    LicenseType,
    PolicyIdentity,
    UnifiedGovernanceService,
    build_governance_review_packet,
)
from apps.read_only_data_gateway_app_1 import ArtifactFormat, RegisteredArtifactRegistry, RegisteredArtifactSource


def _service(*, license_type=LicenseType.PUBLIC, published="2026-07-16T07:59:30Z", credential_status=CredentialReferenceStatus.DECLARED_AVAILABLE):
    source = RegisteredArtifactSource(
        "source-a", "source-evidence-a", "registered/source-a.json", ArtifactFormat.JSON,
        "a" * 64, "RESEARCH", "HIGH", "PUBLIC", "ALLOWED", "FRESH", published,
    )
    license_policy = LicensePolicy(
        "source-a", "source-evidence-a", PolicyIdentity("license-policy-a", "v1", "license-evidence-a"),
        license_type, ("LOCAL_RESEARCH",), retention_days=30,
    )
    freshness_policy = FreshnessPolicy(
        "source-a", "source-evidence-a", PolicyIdentity("freshness-policy-a", "v1", "freshness-evidence-a"),
        60, 300,
    )
    reference = CredentialReferenceMetadata(
        "credential-reference-a", "source-a", "provider-a", "research-read-only",
        PolicyIdentity("credential-policy-a", "v1", "credential-evidence-a"), credential_status,
        "2026-07-16T07:00:00Z", "2026-07-17T07:00:00Z",
    )
    return UnifiedGovernanceService(
        RegisteredArtifactRegistry((source,)),
        LicensePolicyRegistry((license_policy,)),
        FreshnessPolicyRegistry((freshness_policy,)),
        CredentialReferenceRegistry((reference,)),
    )


def _request(source_id="source-a"):
    return GovernanceRequest("request-a", "correlation-a", source_id, "2026-07-16T08:00:00Z", "LOCAL_RESEARCH")


def test_d5_unified_ready_evaluation_contains_all_domains():
    outcome = _service().evaluate(_request(), credential_reference_required=True)
    assert outcome.audit_record.overall_status is GovernanceDecisionStatus.READY_FOR_OPERATOR_REVIEW
    assert len(outcome.audit_record.decisions) == 3
    assert all(len(value) == 64 for value in (
        outcome.license_registry_sha256,
        outcome.freshness_registry_sha256,
        outcome.credential_reference_registry_sha256,
    ))


def test_d5_any_blocked_domain_blocks_overall_status():
    outcome = _service(credential_status=CredentialReferenceStatus.DECLARED_UNAVAILABLE).evaluate(
        _request(), credential_reference_required=True
    )
    assert outcome.audit_record.overall_status is GovernanceDecisionStatus.BLOCKED


def test_d5_aging_source_degrades_overall_status():
    outcome = _service(published="2026-07-16T07:58:00Z").evaluate(
        _request(), credential_reference_required=False
    )
    assert outcome.audit_record.overall_status is GovernanceDecisionStatus.DEGRADED


def test_d5_unregistered_source_fails_closed():
    with pytest.raises(KeyError, match="unregistered source_id"):
        _service().evaluate(_request("missing"), credential_reference_required=False)


def test_d5_service_rejects_invalid_registry_contracts():
    with pytest.raises(TypeError, match="source_registry"):
        UnifiedGovernanceService({}, {}, {}, {})


def test_d5_review_packet_is_immutable_read_only_and_material_free():
    packet = build_governance_review_packet(
        _service().evaluate(_request(), credential_reference_required=True)
    )
    assert packet.payload["overall_status"] == "READY_FOR_OPERATOR_REVIEW"
    assert packet.payload["credential_material_present"] is False
    assert packet.payload["automatic_activation_allowed"] is False
    assert len(packet.payload["decisions"]) == 3
    with pytest.raises(TypeError):
        packet.payload["overall_status"] = "tampered"


def test_d5_review_packet_rejects_wrong_outcome_type():
    with pytest.raises(TypeError, match="GovernanceEvaluationOutcome"):
        build_governance_review_packet({})
