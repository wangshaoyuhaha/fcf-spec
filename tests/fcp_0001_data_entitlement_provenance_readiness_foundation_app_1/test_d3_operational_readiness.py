from apps.fcp_0001_data_entitlement_provenance_readiness_foundation_app_1 import (
    EntitlementEvidenceState,
    EntitlementReviewRequest,
    ExpiryKind,
    FindingSeverity,
    RevocationState,
    SourceEntitlementRecord,
    SourceEntitlementRegistry,
    evaluate_entitlement_coverage,
    evaluate_operational_readiness,
)


def _request() -> EntitlementReviewRequest:
    return EntitlementReviewRequest(
        request_id="request-1",
        correlation_id="correlation-1",
        source_id="registered-source-1",
        evaluated_at_utc="2026-07-19T10:00:00Z",
        intended_use_id="local-research",
        required_field_ids=("close", "open"),
    )


def _record(
    *,
    expiry_kind: ExpiryKind = ExpiryKind.PERPETUAL,
    expires_at_utc: str | None = None,
    revocation_state: RevocationState = RevocationState.ACTIVE,
) -> SourceEntitlementRecord:
    return SourceEntitlementRecord(
        record_id="entitlement-record-1",
        record_version="v1",
        source_id="registered-source-1",
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
        revocation_state=revocation_state,
        evidence_ids=("registered-evidence-1",),
    )


def _evaluate(record: SourceEntitlementRecord):
    coverage = evaluate_entitlement_coverage(
        _request(), SourceEntitlementRegistry((record,))
    )
    return evaluate_operational_readiness(coverage)


def test_complete_operational_metadata_is_informational_only() -> None:
    assessment = _evaluate(_record())
    assert tuple(item.code for item in assessment.findings) == (
        "operational-evidence-complete",
    )
    assert assessment.findings[0].severity is FindingSeverity.INFORMATIONAL


def test_unknown_operational_dimensions_are_all_visible_and_blocking() -> None:
    record = SourceEntitlementRecord(
        record_id="entitlement-record-unknown",
        record_version="v1",
        source_id="registered-source-1",
        evidence_state=EntitlementEvidenceState.REGISTERED,
        market_scope_ids=("a-share",),
        field_ids=("open", "close"),
        permitted_use_ids=("local-research",),
        rights_evidence_ids=("rights-evidence-1",),
        lineage_evidence_ids=("lineage-evidence-1",),
        evidence_ids=("registered-evidence-1",),
    )
    assessment = _evaluate(record)
    codes = tuple(item.code for item in assessment.findings)
    assert codes == tuple(sorted(codes))
    assert "cost-not-researched" in codes
    assert "expiry-not-researched" in codes
    assert "freshness-objective-not-researched" in codes
    assert "latency-objective-not-researched" in codes
    assert "revocation-not-researched" in codes
    assert all(item.severity is FindingSeverity.BLOCKING for item in assessment.findings)


def test_expired_entitlement_is_blocking() -> None:
    assessment = _evaluate(
        _record(
            expiry_kind=ExpiryKind.DATE_BOUND,
            expires_at_utc="2026-07-19T09:59:59Z",
        )
    )
    assert "entitlement-expired" in {item.code for item in assessment.findings}


def test_approaching_expiry_is_degraded() -> None:
    assessment = _evaluate(
        _record(
            expiry_kind=ExpiryKind.DATE_BOUND,
            expires_at_utc="2026-08-01T10:00:00Z",
        )
    )
    finding = next(
        item
        for item in assessment.findings
        if item.code == "entitlement-expiry-approaching"
    )
    assert finding.severity is FindingSeverity.DEGRADED


def test_revoked_entitlement_is_blocking() -> None:
    assessment = _evaluate(_record(revocation_state=RevocationState.REVOKED))
    assert "entitlement-revoked" in {item.code for item in assessment.findings}


def test_dimension_values_require_dimension_evidence() -> None:
    complete = _record()
    record = SourceEntitlementRecord(
        **{
            **complete.__dict__,
            "retention_evidence_ids": (),
            "service_level_evidence_ids": (),
            "cost_evidence_ids": (),
            "expiry_evidence_ids": (),
            "revocation_evidence_ids": (),
        }
    )
    assessment = _evaluate(record)
    assert {item.code for item in assessment.findings} == {
        "cost-evidence-missing",
        "expiry-evidence-missing",
        "retention-evidence-missing",
        "revocation-evidence-missing",
        "service-level-evidence-missing",
    }
