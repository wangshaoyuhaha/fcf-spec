import pytest

from apps.fcp_0001_data_entitlement_provenance_readiness_foundation_app_1 import (
    EntitlementEvidenceState,
    EntitlementReviewRequest,
    ExpiryKind,
    FindingSeverity,
    RevocationState,
    SourceEntitlementRecord,
    SourceEntitlementRegistry,
    evaluate_entitlement_coverage,
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
    field_ids: tuple[str, ...] = ("open", "close"),
) -> SourceEntitlementRecord:
    return SourceEntitlementRecord(
        record_id=f"record-{source_id}",
        record_version="v1",
        source_id=source_id,
        evidence_state=EntitlementEvidenceState.REGISTERED,
        market_scope_ids=("a-share",),
        field_ids=field_ids,
        permitted_use_ids=("local-research",),
        rights_evidence_ids=("rights-evidence-1",),
        lineage_evidence_ids=("lineage-evidence-1",),
        retention_days=30,
        freshness_objective_seconds=60,
        latency_objective_ms=500,
        monthly_cost_minor_units=0,
        currency_code="CNY",
        expiry_kind=ExpiryKind.PERPETUAL,
        revocation_state=RevocationState.ACTIVE,
        evidence_ids=("registered-evidence-1",),
    )


def test_registry_digest_is_independent_of_input_order() -> None:
    first = _record("registered-source-1")
    second = _record("registered-source-2")
    left = SourceEntitlementRegistry((second, first))
    right = SourceEntitlementRegistry((first, second))
    assert left.records == (first, second)
    assert left.registry_sha256 == right.registry_sha256


def test_registry_rejects_duplicate_source() -> None:
    with pytest.raises(ValueError, match="duplicate source entitlement source_id"):
        SourceEntitlementRegistry(
            (
                _record(),
                SourceEntitlementRecord(
                    **{
                        **_record().__dict__,
                        "record_id": "different-record-id",
                    }
                ),
            )
        )


def test_complete_coverage_is_informational_only() -> None:
    assessment = evaluate_entitlement_coverage(
        _request(), SourceEntitlementRegistry((_record(),))
    )
    assert tuple(item.code for item in assessment.findings) == (
        "entitlement-coverage-complete",
    )
    assert assessment.findings[0].severity is FindingSeverity.INFORMATIONAL
    assert len(assessment.registry_sha256) == 64


def test_missing_registry_record_is_explicitly_blocked() -> None:
    assessment = evaluate_entitlement_coverage(
        _request("missing-source"), SourceEntitlementRegistry((_record(),))
    )
    assert assessment.record.evidence_state is EntitlementEvidenceState.MISSING
    assert tuple(item.code for item in assessment.findings) == (
        "entitlement-record-missing",
    )
    assert assessment.findings[0].severity is FindingSeverity.BLOCKING


def test_required_field_gap_is_blocking() -> None:
    assessment = evaluate_entitlement_coverage(
        _request(), SourceEntitlementRegistry((_record(field_ids=("close",)),))
    )
    assert "required-fields-missing" in {
        item.code for item in assessment.findings
    }


def test_not_researched_state_preserves_all_unknowns() -> None:
    record = SourceEntitlementRecord(
        record_id="not-researched-record",
        record_version="v1",
        source_id="registered-source-1",
        evidence_state=EntitlementEvidenceState.NOT_RESEARCHED,
    )
    assessment = evaluate_entitlement_coverage(
        _request(), SourceEntitlementRegistry((record,))
    )
    codes = tuple(item.code for item in assessment.findings)
    assert codes == tuple(sorted(codes))
    assert "entitlement-not-researched" in codes
    assert "intended-use-not-permitted" in codes
    assert "lineage-evidence-missing" in codes
    assert "market-scope-not-researched" in codes
    assert "registered-evidence-missing" in codes
    assert "required-fields-missing" in codes
    assert "retention-not-researched" in codes
    assert "rights-evidence-missing" in codes
    assert all(item.severity is FindingSeverity.BLOCKING for item in assessment.findings)
