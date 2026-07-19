from pathlib import Path
from types import MappingProxyType

from apps.fcp_0001_data_entitlement_provenance_readiness_foundation_app_1 import (
    EntitlementEvidenceState,
    EntitlementReviewRequest,
    ExpiryKind,
    RevocationState,
    SourceEntitlementRecord,
    SourceEntitlementRegistry,
    build_entitlement_readiness_review_packet,
    evaluate_source_readiness,
    validate_entitlement_readiness_acceptance,
)
from scripts.control_center_fcp_0001_data_entitlement_provenance_readiness_guard import (
    APPROVAL_END,
    AUTHORITY_PATHS,
    build_fcp_0001_guard_report,
    validate_fcp_0001_state,
)
from scripts.run_all_checks import COMMANDS


ROOT = Path(__file__).resolve().parents[2]


def _complete_record() -> SourceEntitlementRecord:
    return SourceEntitlementRecord(
        record_id="record-1",
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
        expiry_kind=ExpiryKind.PERPETUAL,
        revocation_state=RevocationState.ACTIVE,
        evidence_ids=("registered-evidence-1",),
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


def test_acceptance_passes_complete_review_packet() -> None:
    outcome = evaluate_source_readiness(
        _request(), SourceEntitlementRegistry((_complete_record(),))
    )
    packet = build_entitlement_readiness_review_packet(outcome)
    report = validate_entitlement_readiness_acceptance(outcome, packet)
    assert report.status == "PASS"
    assert isinstance(report.checks, MappingProxyType)
    assert all(report.checks.values())
    assert report.phase_authorization_allowed is False


def test_acceptance_passes_correctly_blocked_review_packet() -> None:
    outcome = evaluate_source_readiness(
        _request("missing-source"), SourceEntitlementRegistry((_complete_record(),))
    )
    packet = build_entitlement_readiness_review_packet(outcome)
    report = validate_entitlement_readiness_acceptance(outcome, packet)
    assert report.status == "PASS"
    assert report.readiness_status == "BLOCKED"


def test_repository_guard_passes_current_delivery() -> None:
    report = build_fcp_0001_guard_report(ROOT)
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_repository_guard_is_wired_into_all_checks() -> None:
    assert [
        "python",
        "scripts/control_center_fcp_0001_data_entitlement_provenance_readiness_guard.py",
    ] in COMMANDS


def test_guard_detects_authority_divergence() -> None:
    authority_texts = tuple(
        (ROOT / path).read_text(encoding="ascii") for path in AUTHORITY_PATHS
    )
    approval_text = (
        ROOT
        / "FCF_CURRENT_STATE_FCP_0001_DATA_ENTITLEMENT_PROVENANCE_READINESS_FOUNDATION_APP_1_APPROVED.md"
    ).read_text(encoding="ascii")
    import json

    manifest = json.loads(
        (ROOT / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii")
    )
    intake = json.loads(
        (ROOT / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(
            encoding="ascii"
        )
    )
    corrupted = authority_texts[:-1] + (
        authority_texts[-1].replace(APPROVAL_END, "", 1),
    )
    checks = validate_fcp_0001_state(
        corrupted,
        approval_text,
        manifest,
        intake,
        True,
    )
    assert checks["approval_blocks_exact_across_authorities"] is False


def test_guard_detects_research_status_overclaim() -> None:
    authority_texts = tuple(
        (ROOT / path).read_text(encoding="ascii") for path in AUTHORITY_PATHS
    )
    approval_text = (
        ROOT
        / "FCF_CURRENT_STATE_FCP_0001_DATA_ENTITLEMENT_PROVENANCE_READINESS_FOUNDATION_APP_1_APPROVED.md"
    ).read_text(encoding="ascii")
    import json

    manifest = json.loads(
        (ROOT / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii")
    )
    intake = json.loads(
        (ROOT / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(
            encoding="ascii"
        )
    )
    first = next(
        item for item in intake["proposals"] if item["proposal_id"] == "FCF-FCP-0001"
    )
    first["status"] = "IMPLEMENTED"
    checks = validate_fcp_0001_state(
        authority_texts,
        approval_text,
        manifest,
        intake,
        True,
    )
    assert checks["fcp_0001_still_research_only"] is False
