from apps.data_and_credential_governance import (
    CredentialReferenceMetadata,
    CredentialReferenceRegistry,
    CredentialReferenceStatus,
    FreshnessPolicy,
    FreshnessPolicyRegistry,
    GovernanceRequest,
    LicensePolicy,
    LicensePolicyRegistry,
    LicenseType,
    PolicyIdentity,
    UnifiedGovernanceService,
    build_governance_review_packet,
    validate_governance_acceptance,
)
from apps.read_only_data_gateway_app_1 import ArtifactFormat, RegisteredArtifactRegistry, RegisteredArtifactSource


def _outcome_and_packet():
    source = RegisteredArtifactSource(
        "source-a", "source-evidence-a", "registered/source-a.json", ArtifactFormat.JSON,
        "a" * 64, "RESEARCH", "HIGH", "PUBLIC", "ALLOWED", "FRESH", "2026-07-16T08:59:30Z",
    )
    license_policy = LicensePolicy(
        "source-a", "source-evidence-a", PolicyIdentity("license-policy-a", "v1", "license-evidence-a"),
        LicenseType.PUBLIC, ("LOCAL_RESEARCH",), retention_days=30,
    )
    freshness_policy = FreshnessPolicy(
        "source-a", "source-evidence-a", PolicyIdentity("freshness-policy-a", "v1", "freshness-evidence-a"), 60, 300,
    )
    reference = CredentialReferenceMetadata(
        "credential-reference-a", "source-a", "provider-a", "research-read-only",
        PolicyIdentity("credential-policy-a", "v1", "credential-evidence-a"),
        CredentialReferenceStatus.DECLARED_AVAILABLE, "2026-07-16T08:00:00Z", "2026-07-17T08:00:00Z",
    )
    service = UnifiedGovernanceService(
        RegisteredArtifactRegistry((source,)), LicensePolicyRegistry((license_policy,)),
        FreshnessPolicyRegistry((freshness_policy,)), CredentialReferenceRegistry((reference,)),
    )
    request = GovernanceRequest("request-a", "correlation-a", "source-a", "2026-07-16T09:00:00Z", "LOCAL_RESEARCH")
    outcome = service.evaluate(request, credential_reference_required=True)
    return outcome, build_governance_review_packet(outcome)


def test_d6_acceptance_reconciles_all_governance_domains():
    outcome, packet = _outcome_and_packet()
    report = validate_governance_acceptance(outcome, packet)
    assert report.status == "PASS"
    assert report.decision_domains == (
        "CREDENTIAL_REFERENCE", "DATA_FRESHNESS", "SOURCE_LICENSE"
    )


def test_d6_acceptance_preserves_read_only_operator_gate():
    outcome, packet = _outcome_and_packet()
    report = validate_governance_acceptance(outcome, packet)
    assert report.operator_review_required is True
    assert report.read_only is True
    assert report.credential_material_present is False
    assert report.automatic_activation_allowed is False


def test_d6_acceptance_preserves_no_network_no_execution_boundary():
    outcome, packet = _outcome_and_packet()
    report = validate_governance_acceptance(outcome, packet)
    assert report.network_retrieval_allowed is False
    assert report.real_execution_allowed is False
