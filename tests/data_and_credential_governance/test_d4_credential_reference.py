from dataclasses import replace

import pytest

from apps.data_and_credential_governance import (
    CredentialReferenceMetadata,
    CredentialReferenceRegistry,
    CredentialReferenceStatus,
    GovernanceDecisionStatus,
    GovernanceRequest,
    PolicyIdentity,
    evaluate_credential_reference,
)


def _request(source_id="source-a", evaluated="2026-07-16T07:00:00Z"):
    return GovernanceRequest("request-a", "correlation-a", source_id, evaluated, "LOCAL_RESEARCH")


def _reference(**updates):
    values = dict(
        reference_id="credential-reference-a",
        source_id="source-a",
        provider_id="provider-a",
        purpose="research-read-only",
        identity=PolicyIdentity("credential-policy-a", "v1", "credential-evidence-a"),
        status=CredentialReferenceStatus.DECLARED_AVAILABLE,
        observed_at_utc="2026-07-16T06:00:00Z",
        expires_at_utc="2026-07-17T06:00:00Z",
    )
    values.update(updates)
    return CredentialReferenceMetadata(**values)


def test_d4_metadata_contract_rejects_material_and_locator():
    with pytest.raises(ValueError, match="material must never"):
        _reference(credential_material_present=True)
    with pytest.raises(ValueError, match="locator must never"):
        _reference(retrieval_locator_present=True)


def test_d4_metadata_requires_valid_expiry_and_operator_review():
    with pytest.raises(ValueError, match="must be after"):
        _reference(expires_at_utc="2026-07-16T05:00:00Z")
    with pytest.raises(ValueError, match="operator_review_required"):
        _reference(operator_review_required=False)


def test_d4_registry_validates_types_before_sorting_and_is_reproducible():
    with pytest.raises(TypeError, match="CredentialReferenceMetadata"):
        CredentialReferenceRegistry(("invalid",))
    other = _reference(
        reference_id="credential-reference-b",
        source_id="source-b",
        identity=PolicyIdentity("credential-policy-b", "v1", "credential-evidence-b"),
    )
    assert CredentialReferenceRegistry((_reference(), other)).registry_sha256 == CredentialReferenceRegistry((other, _reference())).registry_sha256


def test_d4_registry_rejects_duplicate_source():
    with pytest.raises(ValueError, match="source_id"):
        CredentialReferenceRegistry((_reference(), replace(_reference(), reference_id="credential-reference-b")))


def test_d4_not_required_is_ready_without_reference_access():
    decision = evaluate_credential_reference(_request("missing"), CredentialReferenceRegistry((_reference(),)), credential_reference_required=False)
    assert decision.status is GovernanceDecisionStatus.READY_FOR_OPERATOR_REVIEW


def test_d4_required_missing_reference_is_blocked():
    decision = evaluate_credential_reference(_request("missing"), CredentialReferenceRegistry((_reference(),)), credential_reference_required=True)
    assert decision.status is GovernanceDecisionStatus.BLOCKED
    assert decision.blocking_reasons == ("credential-reference-missing",)


@pytest.mark.parametrize("status,reason", (
    (CredentialReferenceStatus.DECLARED_UNAVAILABLE, "credential-reference-unavailable"),
    (CredentialReferenceStatus.UNKNOWN, "credential-reference-status-unknown"),
))
def test_d4_unavailable_or_unknown_reference_is_blocked(status, reason):
    decision = evaluate_credential_reference(_request(), CredentialReferenceRegistry((_reference(status=status),)), credential_reference_required=True)
    assert decision.status is GovernanceDecisionStatus.BLOCKED
    assert reason in decision.blocking_reasons


def test_d4_expired_reference_is_blocked():
    reference = _reference(expires_at_utc="2026-07-16T06:30:00Z")
    decision = evaluate_credential_reference(_request(), CredentialReferenceRegistry((reference,)), credential_reference_required=True)
    assert decision.status is GovernanceDecisionStatus.BLOCKED
    assert decision.blocking_reasons == ("credential-reference-expired",)


def test_d4_available_reference_is_reviewable_but_not_activated():
    decision = evaluate_credential_reference(_request(), CredentialReferenceRegistry((_reference(),)), credential_reference_required=True)
    assert decision.status is GovernanceDecisionStatus.READY_FOR_OPERATOR_REVIEW
    assert decision.automatic_activation_allowed is False
