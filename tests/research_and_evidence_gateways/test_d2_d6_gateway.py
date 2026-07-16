import pytest

from apps.research_and_evidence_gateways import (
    CrossVerificationStatus, EvidenceTrace, ResearchGatewayService, ResearchQuery,
    ResearchSource, ResearchSourceRegistry, RetrievalReceipt, SourceClass,
    validate_research_acceptance,
)


def _source(**updates):
    values=dict(source_id="source-a", source_url="https://research.example.com/report", source_class=SourceClass.A, trust_level="HIGH", license_policy_id="license-a", freshness_policy_id="fresh-a", evidence_id="evidence-a")
    values.update(updates); return ResearchSource(**values)


def _query(): return ResearchQuery("query-a", "correlation-a", "BTC evidence", "2026-07-16T11:00:00Z", ("source-a",))


def _receipt(**updates):
    values=dict(receipt_id="receipt-a", query_id="query-a", source_id="source-a", evidence_id="evidence-a", registered_artifact_id="artifact-a", content_sha256="a"*64, publication_at_utc="2026-07-16T09:00:00Z", retrieved_at_utc="2026-07-16T10:00:00Z", quoted_location="section-1")
    values.update(updates); return RetrievalReceipt(**values)


def _trace(status=CrossVerificationStatus.VERIFIED):
    return EvidenceTrace(_receipt(), _source(), status, ("support-evidence-a",) if status is CrossVerificationStatus.VERIFIED else ())


def test_d2_registry_is_reproducible_and_fail_closed():
    other=_source(source_id="source-b", source_url="https://research.example.com/other", evidence_id="evidence-b")
    assert ResearchSourceRegistry((_source(),other)).registry_sha256 == ResearchSourceRegistry((other,_source())).registry_sha256
    with pytest.raises(TypeError, match="ResearchSource"): ResearchSourceRegistry(("invalid",))
    with pytest.raises(KeyError, match="unregistered"): ResearchSourceRegistry((_source(),)).require("missing")


def test_d3_receipt_rejects_bad_digest_credentials_and_transport():
    with pytest.raises(ValueError, match="SHA-256"): _receipt(content_sha256="bad")
    with pytest.raises(ValueError, match="without credentials"): _receipt(credential_material_present=True)
    with pytest.raises(ValueError, match="without credentials"): _receipt(network_transport_performed=True)


def test_d4_trace_requires_linkage_and_verified_support():
    with pytest.raises(ValueError, match="linkage"): EvidenceTrace(_receipt(source_id="other"), _source(), CrossVerificationStatus.PARTIAL, ())
    with pytest.raises(ValueError, match="supporting evidence"): EvidenceTrace(_receipt(), _source(), CrossVerificationStatus.VERIFIED, ())


def test_d5_service_builds_read_only_operator_packet():
    service=ResearchGatewayService(ResearchSourceRegistry((_source(),)))
    outcome=service.evaluate(_query(), (_trace(),))
    packet=service.build_review_packet(outcome)
    assert outcome.status == "READY_FOR_OPERATOR_REVIEW"
    assert packet.payload["read_only"] is True
    assert packet.payload["credential_material_present"] is False
    with pytest.raises(TypeError): packet.payload["status"]="tampered"


def test_d5_unverified_trace_is_visible_degradation():
    service=ResearchGatewayService(ResearchSourceRegistry((_source(),)))
    assert service.evaluate(_query(), (_trace(CrossVerificationStatus.UNVERIFIED),)).status == "DEGRADED"


def test_d5_rejects_unapproved_trace():
    bad=EvidenceTrace(_receipt(source_id="source-b", evidence_id="evidence-b"), _source(source_id="source-b", source_url="https://research.example.com/b", evidence_id="evidence-b"), CrossVerificationStatus.PARTIAL, ())
    with pytest.raises(ValueError, match="approval linkage"):
        ResearchGatewayService(ResearchSourceRegistry((_source(),))).evaluate(_query(), (bad,))


def test_d6_acceptance_preserves_boundaries():
    service=ResearchGatewayService(ResearchSourceRegistry((_source(),)))
    outcome=service.evaluate(_query(), (_trace(),))
    assert validate_research_acceptance(outcome, service.build_review_packet(outcome)) == "PASS"
