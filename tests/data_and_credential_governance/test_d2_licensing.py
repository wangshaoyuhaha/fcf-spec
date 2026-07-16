from dataclasses import replace
from types import MappingProxyType

import pytest

from apps.data_and_credential_governance import (
    GovernanceDecisionStatus,
    GovernanceRequest,
    LicensePolicy,
    LicensePolicyRegistry,
    LicenseType,
    PolicyIdentity,
    evaluate_source_license,
)


def _request(intended_use="LOCAL_RESEARCH", source_id="source-a"):
    return GovernanceRequest("request-a", "correlation-a", source_id, "2026-07-16T05:00:00Z", intended_use)


def _policy(**updates):
    values = {
        "source_id": "source-a",
        "source_evidence_id": "source-evidence-a",
        "identity": PolicyIdentity("license-policy-a", "v1", "policy-evidence-a"),
        "license_type": LicenseType.PUBLIC,
        "allowed_uses": ("LOCAL_RESEARCH",),
        "retention_days": 30,
    }
    values.update(updates)
    return LicensePolicy(**values)


def test_d2_policy_payload_is_immutable_and_normalized():
    policy = _policy(allowed_uses=("local_research", "LOCAL_RESEARCH"))
    assert policy.allowed_uses == ("LOCAL_RESEARCH",)
    assert isinstance(policy.as_payload(), MappingProxyType)
    with pytest.raises(TypeError):
        policy.as_payload()["license_type"] = "tampered"


def test_d2_unknown_and_prohibited_licenses_cannot_grant_external_use():
    with pytest.raises(ValueError, match="cannot grant external usage"):
        _policy(license_type=LicenseType.UNKNOWN, cloud_processing_allowed=True)
    with pytest.raises(ValueError, match="cannot allow a use"):
        _policy(license_type=LicenseType.PROHIBITED)


def test_d2_retention_and_operator_review_are_fail_closed():
    with pytest.raises(ValueError, match="positive integer"):
        _policy(retention_days=0)
    with pytest.raises(ValueError, match="operator_review_required"):
        _policy(operator_review_required=False)


def test_d2_registry_is_sorted_reproducible_and_immutable():
    policy_b = _policy(
        source_id="source-b",
        source_evidence_id="source-evidence-b",
        identity=PolicyIdentity("license-policy-b", "v1", "policy-evidence-b"),
    )
    first = LicensePolicyRegistry((policy_b, _policy()))
    second = LicensePolicyRegistry((_policy(), policy_b))
    assert tuple(item.source_id for item in first.policies) == ("source-a", "source-b")
    assert first.registry_sha256 == second.registry_sha256


def test_d2_registry_rejects_empty_duplicates_and_invalid_entries():
    with pytest.raises(ValueError, match="must not be empty"):
        LicensePolicyRegistry(())
    with pytest.raises(ValueError, match="source_id"):
        LicensePolicyRegistry((_policy(), _policy()))
    with pytest.raises(TypeError, match="LicensePolicy"):
        LicensePolicyRegistry(("invalid",))


def test_d2_missing_policy_returns_blocked_decision():
    decision = evaluate_source_license(_request(source_id="missing"), LicensePolicyRegistry((_policy(),)))
    assert decision.status is GovernanceDecisionStatus.BLOCKED
    assert decision.blocking_reasons == ("license-policy-missing",)


def test_d2_public_local_research_is_ready_for_review():
    decision = evaluate_source_license(_request(), LicensePolicyRegistry((_policy(),)))
    assert decision.status is GovernanceDecisionStatus.READY_FOR_OPERATOR_REVIEW
    assert decision.evidence_ids == ("policy-evidence-a", "source-evidence-a")


def test_d2_prohibited_license_is_blocked():
    policy = replace(_policy(), license_type=LicenseType.PROHIBITED, allowed_uses=())
    decision = evaluate_source_license(_request(), LicensePolicyRegistry((policy,)))
    assert decision.status is GovernanceDecisionStatus.BLOCKED
    assert "license-prohibited" in decision.blocking_reasons


@pytest.mark.parametrize("intended_use,reason", (
    ("CLOUD_PROCESSING", "cloud-processing-not-licensed"),
    ("REDISTRIBUTION", "redistribution-not-licensed"),
    ("MODEL_TRAINING", "training-not-licensed"),
))
def test_d2_external_usage_is_blocked_without_explicit_permission(intended_use, reason):
    policy = _policy(allowed_uses=(intended_use,))
    decision = evaluate_source_license(_request(intended_use), LicensePolicyRegistry((policy,)))
    assert decision.status is GovernanceDecisionStatus.BLOCKED
    assert reason in decision.blocking_reasons


def test_d2_unknown_local_license_is_degraded_and_reviewable():
    policy = _policy(license_type=LicenseType.UNKNOWN, retention_days=None)
    decision = evaluate_source_license(_request(), LicensePolicyRegistry((policy,)))
    assert decision.status is GovernanceDecisionStatus.DEGRADED
    assert decision.degradation_reasons == ("license-unknown", "retention-policy-restricted")


def test_d2_restricted_explicit_use_is_degraded():
    decision = evaluate_source_license(
        _request(), LicensePolicyRegistry((_policy(license_type=LicenseType.RESTRICTED),))
    )
    assert decision.status is GovernanceDecisionStatus.DEGRADED
    assert decision.degradation_reasons == ("license-restricted",)


def test_d2_evaluator_rejects_wrong_contract_types():
    registry = LicensePolicyRegistry((_policy(),))
    with pytest.raises(TypeError, match="GovernanceRequest"):
        evaluate_source_license({}, registry)
    with pytest.raises(TypeError, match="LicensePolicyRegistry"):
        evaluate_source_license(_request(), {})
