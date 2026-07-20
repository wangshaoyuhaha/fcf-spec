from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from types import MappingProxyType

import pytest

from apps.browser_product_console_runtime_app_1 import (
    BrowserProductConsoleApplication,
    ConsoleReadModel,
)
from apps.fcp_0008_chinese_browser_console_local_data_intake_preview_app_1 import (
    ConsoleLocale,
    LocalizedBrowserConsoleApplication,
)
from apps.fcp_0009_provider_neutral_market_data_adapter_readiness_app_1 import (
    MarketDataDiagnosticsConsoleApplication,
    build_registered_local_replay_fixture,
)
from apps.fcp_0010_simplified_chinese_console_localization_consistency_app_1 import (
    SimplifiedChineseConsoleApplication,
)
from apps.fcp_0011_candidate_data_source_onboarding_evidence_review_app_1 import (
    CandidateDataSourceOnboardingApplication,
    build_operator_declared_candidate_profiles,
)
from apps.fcp_0012_sanitized_candidate_data_session_evidence_intake_app_1 import (
    SanitizedSessionEvidenceApplication,
    load_rqdata_trial_session,
)
from apps.fcp_0013_candidate_data_evidence_bundle_reconciliation_app_1 import (
    CandidateEvidenceBundleApplication,
    load_candidate_evidence_bundle,
    load_rqdata_candidate_bundle_review,
)
from apps.fcp_0014_candidate_data_evidence_gap_remediation_plan_app_1 import (
    FCP_0014_BOUNDARY,
    EvidenceGapRemediationApplication,
    EvidenceGapRemediationBoundary,
    build_candidate_evidence_gap_remediation_plan,
    load_rqdata_candidate_remediation_plan,
)
from scripts.run_fcp_0014_candidate_evidence_gap_remediation import main


ROOT = Path(__file__).resolve().parents[2]


def _application() -> EvidenceGapRemediationApplication:
    model = ConsoleReadModel(
        correlation_id="corr-fcp-0014-test",
        candidates=(),
        sections=MappingProxyType({}),
        source_artifact_ids=(),
    )
    localized = LocalizedBrowserConsoleApplication(
        BrowserProductConsoleApplication(model),
        ConsoleLocale("en"),
    )
    _, snapshot = build_registered_local_replay_fixture()
    diagnostics = MarketDataDiagnosticsConsoleApplication(localized, snapshot)
    chinese = SimplifiedChineseConsoleApplication(diagnostics)
    profiles = build_operator_declared_candidate_profiles()
    onboarding = CandidateDataSourceOnboardingApplication(chinese, profiles)
    profile, registration, evidence = load_rqdata_trial_session(ROOT)
    session = SanitizedSessionEvidenceApplication(onboarding, profile, registration, evidence)
    bundle = load_candidate_evidence_bundle(ROOT)
    reconciliation = CandidateEvidenceBundleApplication(session, bundle)
    _, _, plan = load_rqdata_candidate_remediation_plan(ROOT)
    return EvidenceGapRemediationApplication(reconciliation, plan)


def test_d1_boundary_is_closed_and_immutable() -> None:
    assert FCP_0014_BOUNDARY.local_only is True
    assert FCP_0014_BOUNDARY.registered_artifact_only is True
    assert FCP_0014_BOUNDARY.network_allowed is False
    assert FCP_0014_BOUNDARY.credentials_allowed is False
    assert FCP_0014_BOUNDARY.procurement_allowed is False
    assert FCP_0014_BOUNDARY.execution_allowed is False
    with pytest.raises(FrozenInstanceError):
        FCP_0014_BOUNDARY.local_only = False  # type: ignore[misc]


@pytest.mark.parametrize(
    "update",
    (
        {"network_allowed": True},
        {"credentials_allowed": True},
        {"provider_contact_allowed": True},
        {"procurement_allowed": True},
        {"provider_selection_allowed": True},
        {"entitlement_approval_allowed": True},
        {"gap_closure_allowed": True},
        {"realtime_activation_allowed": True},
        {"execution_allowed": True},
        {"operator_review_required": False},
    ),
)
def test_d1_boundary_rejects_added_authority(update: dict[str, bool]) -> None:
    with pytest.raises(ValueError, match="cannot"):
        replace(EvidenceGapRemediationBoundary(), **update)


def test_d2_plan_binds_exact_fcp_0013_packet() -> None:
    _, packet = load_rqdata_candidate_bundle_review(ROOT)
    _, loaded_packet, plan = load_rqdata_candidate_remediation_plan(ROOT)
    assert loaded_packet == packet
    assert plan.source_packet_sha256 == packet.packet_sha256
    assert plan.candidate_id == packet.candidate_id


def test_d3_plan_is_deterministic_and_complete() -> None:
    _, packet = load_rqdata_candidate_bundle_review(ROOT)
    first = build_candidate_evidence_gap_remediation_plan(packet)
    second = build_candidate_evidence_gap_remediation_plan(packet)
    assert first == second
    assert len(first.plan_sha256) == 64
    assert len(first.requirements) == 15
    assert sum(item.priority == "P0" for item in first.requirements) == 6
    assert sum(item.priority == "P1" for item in first.requirements) == 8
    assert sum(item.priority == "P2" for item in first.requirements) == 1


def test_d3_provider_selection_depends_on_governance_evidence() -> None:
    _, _, plan = load_rqdata_candidate_remediation_plan(ROOT)
    item = next(value for value in plan.requirements if value.category == "provider-selection-evidence")
    assert item.priority == "P0"
    assert item.blocker_kind == "GOVERNANCE"
    assert set(item.dependency_ids) == {
        "gap-commercial-entitlement",
        "gap-permitted-use",
        "gap-retention",
        "gap-retention-rights",
        "gap-rights",
    }


def test_d4_all_requirements_remain_open_and_operator_gated() -> None:
    _, _, plan = load_rqdata_candidate_remediation_plan(ROOT)
    assert plan.plan_state == "EVIDENCE_GAPS_OPEN"
    assert plan.external_activation_state == "BLOCKED"
    assert plan.provider_selection_state == "UNSELECTED"
    assert plan.network_state == "DISABLED"
    assert all(item.evidence_state == "MISSING" for item in plan.requirements)
    assert all(item.completion_state == "OPEN" for item in plan.requirements)
    assert all(item.action_state == "OPERATOR_INPUT_REQUIRED" for item in plan.requirements)


def test_d4_canonical_field_requirements_are_exact() -> None:
    _, _, plan = load_rqdata_candidate_remediation_plan(ROOT)
    fields = {
        item.category: item.required_fields
        for item in plan.requirements
        if item.required_fields
    }
    assert set(fields) == {
        "minute-bar-canonical-fields",
        "order-book-canonical-fields",
        "tick-canonical-fields",
    }
    assert "interval" in fields["minute-bar-canonical-fields"]
    assert "bid_price_1" in fields["order-book-canonical-fields"]
    assert "last" in fields["tick-canonical-fields"]


def test_d4_payload_is_immutable_and_contains_no_secret_values() -> None:
    _, _, plan = load_rqdata_candidate_remediation_plan(ROOT)
    assert isinstance(plan.as_payload(), MappingProxyType)
    with pytest.raises(TypeError):
        plan.as_payload()["network_state"] = "ENABLED"  # type: ignore[index]
    text = str(dict(plan.as_payload())).lower()
    assert "password" not in text and "access_token" not in text


def test_d5_chinese_page_is_default_and_read_only() -> None:
    response = _application().dispatch("GET", "/data-source-evidence-remediation")
    body = response.body.decode("ascii")
    assert response.status == 200
    assert ("Content-Language", "zh-CN") in response.headers
    assert "&#25968;" in body
    assert "EVIDENCE_GAPS_OPEN" in body and "BLOCKED" in body
    assert "<form" not in body and "<button" not in body and "<script" not in body


def test_d5_english_head_write_and_delegation_contracts() -> None:
    app = _application()
    english = app.dispatch("GET", "/data-source-evidence-remediation?lang=en")
    head = app.dispatch("HEAD", "/data-source-evidence-remediation")
    post = app.dispatch("POST", "/data-source-evidence-remediation")
    delegated = app.dispatch("GET", "/data-source-evidence-bundle?lang=zh-CN")
    assert english.status == 200 and b"Candidate Data Evidence Gap Remediation Plan" in english.body
    assert head.status == 200 and head.body == b""
    assert post.status == 405 and ("Allow", "GET, HEAD") in post.headers
    assert delegated.status == 200


@pytest.mark.parametrize(
    "path",
    (
        "/data-source-evidence-remediation?lang=unsafe",
        "/data-source-evidence-remediation?lang=en&lang=zh-CN",
    ),
)
def test_d5_invalid_locale_is_rejected(path: str) -> None:
    assert _application().dispatch("GET", path).status == 400


def test_d6_review_json_is_local_safe_and_blocked(capsys) -> None:
    assert main(["--review-json"]) == 0
    output = capsys.readouterr().out
    assert '"open_count": 15' in output
    assert '"external_activation_state": "BLOCKED"' in output
    assert '"network_state": "DISABLED"' in output
    assert "http://" not in output and "https://" not in output


def test_d6_startup_preflight_passes() -> None:
    assert main(["--check", "--port", "18767", "--no-browser"]) == 0


def test_d6_sources_are_ascii_and_provider_free() -> None:
    source_root = ROOT / "apps/fcp_0014_candidate_data_evidence_gap_remediation_plan_app_1"
    combined = ""
    for path in source_root.glob("*.py"):
        combined += path.read_text(encoding="ascii").lower()
    assert "import rqdatac" not in combined
    assert "import rqsdk" not in combined
    assert "import requests" not in combined
    assert "urllib.request" not in combined
