from dataclasses import replace
from types import MappingProxyType

import pytest

from apps.data_and_credential_governance import (
    DATA_AND_CREDENTIAL_GOVERNANCE_BOUNDARY,
    GovernanceAuditRecord,
    GovernanceDecision,
    GovernanceDecisionStatus,
    GovernanceDomain,
    GovernanceRequest,
    PolicyIdentity,
)


def _policy() -> PolicyIdentity:
    return PolicyIdentity("license-policy-a", "v1", "policy-evidence-a")


def _request(**updates) -> GovernanceRequest:
    values = {
        "request_id": "request-001",
        "correlation_id": "correlation-001",
        "source_id": "source-001",
        "evaluated_at_utc": "2026-07-16T04:00:00Z",
        "intended_use": "research",
    }
    values.update(updates)
    return GovernanceRequest(**values)


def _decision(domain=GovernanceDomain.SOURCE_LICENSE, **updates):
    values = {
        "domain": domain,
        "source_id": "source-001",
        "policy": _policy(),
        "status": GovernanceDecisionStatus.READY_FOR_OPERATOR_REVIEW,
        "evidence_ids": ("source-evidence-a",),
    }
    values.update(updates)
    return GovernanceDecision(**values)


def test_d1_boundary_preserves_read_only_authorities():
    boundary = DATA_AND_CREDENTIAL_GOVERNANCE_BOUNDARY
    assert boundary.paper_only is True
    assert boundary.local_only is True
    assert boundary.loopback_only is True
    assert boundary.sidecar_only is True
    assert boundary.read_only is True
    assert boundary.operator_review_required is True
    assert boundary.deterministic_authority_preserved is True
    assert boundary.registered_evidence_authority_preserved is True
    assert boundary.credential_reference_metadata_allowed is True


@pytest.mark.parametrize(
    "field_name",
    (
        "credential_material_allowed",
        "secret_value_allowed",
        "environment_secret_read_allowed",
        "file_secret_read_allowed",
        "network_retrieval_allowed",
        "authenticated_request_allowed",
        "order_path_allowed",
        "real_execution_allowed",
    ),
)
def test_d1_boundary_rejects_prohibited_capabilities(field_name):
    with pytest.raises(ValueError, match="prohibited governance capability"):
        replace(DATA_AND_CREDENTIAL_GOVERNANCE_BOUNDARY, **{field_name: True})


def test_d1_boundary_rejects_disabled_review_or_authority():
    with pytest.raises(ValueError, match="authority flags"):
        replace(DATA_AND_CREDENTIAL_GOVERNANCE_BOUNDARY, operator_review_required=False)


def test_d1_policy_identity_is_normalized_and_immutable():
    policy = _policy()
    payload = policy.as_payload()
    assert isinstance(payload, MappingProxyType)
    assert payload["policy_id"] == "license-policy-a"
    with pytest.raises(TypeError):
        payload["policy_id"] = "tampered"


@pytest.mark.parametrize("value", ("", "unsafe value", "../unsafe", "@unsafe"))
def test_d1_policy_identity_rejects_unsafe_values(value):
    with pytest.raises(ValueError, match="safe identifier"):
        PolicyIdentity(value, "v1", "evidence-a")


def test_d1_request_normalizes_use_and_requires_exact_loopback():
    request = _request()
    assert request.intended_use == "RESEARCH"
    assert request.peer_host == "127.0.0.1"
    with pytest.raises(ValueError, match="exactly 127.0.0.1"):
        replace(request, peer_host="localhost")


def test_d1_request_requires_utc_and_operator_review():
    with pytest.raises(ValueError, match="must be UTC"):
        _request(evaluated_at_utc="2026-07-16T12:00:00+08:00")
    with pytest.raises(ValueError, match="operator_review_required"):
        _request(operator_review_required=False)


def test_d1_ready_decision_is_deterministic_and_immutable():
    decision = _decision(evidence_ids=("evidence-b", "evidence-a", "evidence-b"))
    assert decision.evidence_ids == ("evidence-a", "evidence-b")
    assert decision.automatic_activation_allowed is False
    with pytest.raises(Exception):
        decision.source_id = "tampered"


def test_d1_blocked_decision_requires_reason():
    with pytest.raises(ValueError, match="requires a reason"):
        _decision(status=GovernanceDecisionStatus.BLOCKED)
    decision = _decision(
        status=GovernanceDecisionStatus.BLOCKED,
        blocking_reasons=("license-prohibited", "license-prohibited"),
    )
    assert decision.blocking_reasons == ("license-prohibited",)


def test_d1_non_blocked_decision_rejects_blocking_reason():
    with pytest.raises(ValueError, match="non-blocked"):
        _decision(blocking_reasons=("unexpected",))


def test_d1_ready_decision_rejects_degradation_reason():
    with pytest.raises(ValueError, match="ready governance"):
        _decision(degradation_reasons=("aging",))


def test_d1_decision_rejects_automatic_activation():
    with pytest.raises(ValueError, match="automatic_activation_allowed"):
        _decision(automatic_activation_allowed=True)


def test_d1_audit_record_sorts_domains_and_derives_overall_status():
    freshness = _decision(
        GovernanceDomain.DATA_FRESHNESS,
        policy=PolicyIdentity("freshness-policy-a", "v1", "policy-evidence-b"),
        status=GovernanceDecisionStatus.DEGRADED,
        degradation_reasons=("source-aging",),
    )
    record = GovernanceAuditRecord(_request(), (freshness, _decision()))
    assert tuple(item.domain for item in record.decisions) == (
        GovernanceDomain.DATA_FRESHNESS,
        GovernanceDomain.SOURCE_LICENSE,
    )
    assert record.overall_status is GovernanceDecisionStatus.DEGRADED


def test_d1_audit_record_rejects_duplicate_domain_and_linkage_mismatch():
    with pytest.raises(ValueError, match="duplicate governance domains"):
        GovernanceAuditRecord(_request(), (_decision(), _decision()))
    with pytest.raises(ValueError, match="source linkage mismatch"):
        GovernanceAuditRecord(_request(), (_decision(source_id="source-002"),))
