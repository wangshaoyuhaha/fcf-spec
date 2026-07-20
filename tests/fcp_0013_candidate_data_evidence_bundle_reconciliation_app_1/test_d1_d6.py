import json
import shutil
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
    FCP_0013_BOUNDARY,
    CandidateEvidenceBundleApplication,
    CandidateEvidenceBundleBoundary,
    canonical_json_sha256,
    load_candidate_evidence_bundle,
    load_rqdata_candidate_bundle_review,
    reconcile_candidate_evidence_bundle,
)
from scripts.run_fcp_0013_candidate_evidence_bundle import main


ROOT = Path(__file__).resolve().parents[2]
BUNDLE_REGISTRY = "FCF_REGISTERED_EVIDENCE_FCP_0013_RQDATA_CANDIDATE_BUNDLE.json"
SOURCE_FILES = (
    BUNDLE_REGISTRY,
    "FCF_REGISTERED_EVIDENCE_FCP_0007_RQDATA_A_SHARE_DAILY_DEMO.json",
    "FCF_REGISTERED_EVIDENCE_FCP_0012_RQDATA_TRIAL_SESSION.json",
    "FCF_LOCAL_ARTIFACT_FCP_0012_RQDATA_TRIAL_SESSION.json",
)


def _copy_bundle_fixture(tmp_path: Path) -> Path:
    for name in SOURCE_FILES:
        shutil.copyfile(ROOT / name, tmp_path / name)
    return tmp_path


def _application() -> CandidateEvidenceBundleApplication:
    model = ConsoleReadModel(
        correlation_id="corr-fcp-0013-test",
        candidates=(),
        sections=MappingProxyType({}),
        source_artifact_ids=(),
    )
    localized = LocalizedBrowserConsoleApplication(
        base_application=BrowserProductConsoleApplication(model),
        default_locale=ConsoleLocale("en"),
    )
    _, snapshot = build_registered_local_replay_fixture()
    diagnostics = MarketDataDiagnosticsConsoleApplication(localized, snapshot)
    chinese = SimplifiedChineseConsoleApplication(diagnostics)
    profiles = build_operator_declared_candidate_profiles()
    onboarding = CandidateDataSourceOnboardingApplication(chinese, profiles)
    profile, registration, evidence = load_rqdata_trial_session(ROOT)
    session = SanitizedSessionEvidenceApplication(
        onboarding,
        profile,
        registration,
        evidence,
    )
    return CandidateEvidenceBundleApplication(session, load_candidate_evidence_bundle(ROOT))


def test_d1_boundary_is_closed_and_immutable() -> None:
    assert FCP_0013_BOUNDARY.paper_only is True
    assert FCP_0013_BOUNDARY.registered_artifact_only is True
    assert FCP_0013_BOUNDARY.network_allowed is False
    assert FCP_0013_BOUNDARY.raw_provider_bytes_allowed is False
    assert FCP_0013_BOUNDARY.execution_allowed is False
    with pytest.raises(FrozenInstanceError):
        FCP_0013_BOUNDARY.local_only = False  # type: ignore[misc]


@pytest.mark.parametrize(
    "update",
    (
        {"network_allowed": True},
        {"credentials_allowed": True},
        {"raw_provider_bytes_allowed": True},
        {"provider_selection_allowed": True},
        {"entitlement_approval_allowed": True},
        {"gap_closure_allowed": True},
        {"product_phase_authorization_allowed": True},
        {"execution_allowed": True},
        {"operator_review_required": False},
    ),
)
def test_d1_boundary_rejects_added_authority(update: dict[str, bool]) -> None:
    with pytest.raises(ValueError, match="cannot"):
        replace(CandidateEvidenceBundleBoundary(), **update)


def test_d2_registered_bundle_and_source_digests_load_exactly() -> None:
    registry = json.loads((ROOT / BUNDLE_REGISTRY).read_text(encoding="ascii"))
    bundle = load_candidate_evidence_bundle(ROOT)
    assert bundle.bundle_id == "rqdata-candidate-evidence-bundle-v1"
    assert len(bundle.references) == 2
    for row in registry["bundle"]["source_evidence"]:
        source = json.loads((ROOT / row["registry_path"]).read_text(encoding="ascii"))
        assert canonical_json_sha256(source) == row["canonical_json_sha256"]


def test_d2_loader_never_requires_raw_demo_csv(tmp_path: Path) -> None:
    bundle = load_candidate_evidence_bundle(_copy_bundle_fixture(tmp_path))
    assert bundle.references[0].evidence_kind == "HISTORICAL_DAILY_DEMO"


def test_d2_duplicate_bundle_json_key_is_rejected(tmp_path: Path) -> None:
    root = _copy_bundle_fixture(tmp_path)
    (root / BUNDLE_REGISTRY).write_text('{"schema_version":1,"schema_version":1}', encoding="ascii")
    with pytest.raises(ValueError, match="duplicate"):
        load_candidate_evidence_bundle(root)


def test_d2_source_digest_mismatch_is_rejected(tmp_path: Path) -> None:
    root = _copy_bundle_fixture(tmp_path)
    registry = json.loads((root / BUNDLE_REGISTRY).read_text(encoding="ascii"))
    registry["bundle"]["source_evidence"][0]["canonical_json_sha256"] = "0" * 64
    (root / BUNDLE_REGISTRY).write_text(json.dumps(registry, sort_keys=True), encoding="ascii")
    with pytest.raises(ValueError, match="digest"):
        load_candidate_evidence_bundle(root)


def test_d2_source_identity_mismatch_is_rejected(tmp_path: Path) -> None:
    root = _copy_bundle_fixture(tmp_path)
    source_name = "FCF_REGISTERED_EVIDENCE_FCP_0007_RQDATA_A_SHARE_DAILY_DEMO.json"
    source = json.loads((root / source_name).read_text(encoding="ascii"))
    source["evidence_id"] = "fcp-0007-other-evidence-v1"
    (root / source_name).write_text(json.dumps(source, sort_keys=True), encoding="ascii")
    registry = json.loads((root / BUNDLE_REGISTRY).read_text(encoding="ascii"))
    registry["bundle"]["source_evidence"][0]["canonical_json_sha256"] = canonical_json_sha256(source)
    (root / BUNDLE_REGISTRY).write_text(json.dumps(registry, sort_keys=True), encoding="ascii")
    with pytest.raises(ValueError, match="identity"):
        load_candidate_evidence_bundle(root)


def test_d3_reconciliation_preserves_identity_lineage_and_context() -> None:
    bundle, packet = load_rqdata_candidate_bundle_review(ROOT)
    assert packet.candidate_id == bundle.candidate_id == "candidate-rqdata"
    assert packet.source_evidence_ids == tuple(item.evidence_id for item in bundle.references)
    assert packet.capability_overlap == ("DAILY_BAR",)
    assert packet.conflict_codes == ()
    assert packet.context_codes == ("NON_OVERLAPPING_OBSERVATION_WINDOWS",)


def test_d3_bundle_and_packet_mappings_are_immutable() -> None:
    bundle, packet = load_rqdata_candidate_bundle_review(ROOT)
    assert isinstance(bundle.missing_fields_by_kind, MappingProxyType)
    assert isinstance(packet.as_payload(), MappingProxyType)
    with pytest.raises(TypeError):
        packet.as_payload()["network_state"] = "ENABLED"  # type: ignore[index]


def test_d4_reconciliation_is_deterministic_and_remains_blocked() -> None:
    bundle = load_candidate_evidence_bundle(ROOT)
    first = reconcile_candidate_evidence_bundle(bundle)
    second = reconcile_candidate_evidence_bundle(bundle)
    assert first == second
    assert len(first.packet_sha256) == 64
    assert first.readiness_delta == "EVIDENCE_EXPANDED_NOT_READY"
    assert first.external_activation_state == "BLOCKED"
    assert first.provider_selection_state == "UNSELECTED"
    assert first.entitlement_state == "UNRESOLVED"
    assert first.network_state == "DISABLED"


def test_d4_field_and_documentary_gaps_remain_open() -> None:
    _, packet = load_rqdata_candidate_bundle_review(ROOT)
    assert set(packet.missing_fields_by_kind) == {"MINUTE_BAR", "ORDER_BOOK", "TICK"}
    assert "commercial-entitlement" in packet.missing_evidence_categories
    assert "provider-selection-evidence" in packet.missing_evidence_categories
    assert "realtime-coverage" in packet.missing_evidence_categories
    assert "retention-rights" in packet.missing_evidence_categories


def test_d5_chinese_page_is_default_ascii_and_read_only() -> None:
    response = _application().dispatch("GET", "/data-source-evidence-bundle")
    body = response.body.decode("ascii")
    assert response.status == 200
    assert ("Content-Language", "zh-CN") in response.headers
    assert "&#20505;" in body
    assert "EVIDENCE_EXPANDED_NOT_READY" in body and "BLOCKED" in body
    assert "000001.XSHE" not in body
    assert "<form" not in body and "<button" not in body and "<script" not in body


def test_d5_english_head_write_and_delegation_contracts() -> None:
    app = _application()
    english = app.dispatch("GET", "/data-source-evidence-bundle?lang=en")
    head = app.dispatch("HEAD", "/data-source-evidence-bundle")
    post = app.dispatch("POST", "/data-source-evidence-bundle")
    delegated = app.dispatch("GET", "/data-source-session-evidence?lang=zh-CN")
    assert english.status == 200 and b"Candidate Data Evidence Bundle Reconciliation" in english.body
    assert head.status == 200 and head.body == b""
    assert post.status == 405 and ("Allow", "GET, HEAD") in post.headers
    assert delegated.status == 200


@pytest.mark.parametrize(
    "path",
    (
        "/data-source-evidence-bundle?lang=unsafe",
        "/data-source-evidence-bundle?lang=en&lang=zh-CN",
    ),
)
def test_d5_invalid_locale_is_rejected(path: str) -> None:
    assert _application().dispatch("GET", path).status == 400


def test_d6_local_review_json_is_safe_and_non_networked(capsys) -> None:
    assert main(["--review-json"]) == 0
    output = capsys.readouterr().out
    assert '"readiness_delta": "EVIDENCE_EXPANDED_NOT_READY"' in output
    assert '"external_activation_state": "BLOCKED"' in output
    assert '"network_state": "DISABLED"' in output
    assert "000001.XSHE" not in output
    assert "http://" not in output and "https://" not in output


def test_d6_startup_preflight_passes_on_free_port() -> None:
    assert main(["--check", "--port", "18766", "--no-browser"]) == 0


def test_d6_sources_and_registered_json_are_ascii_and_provider_free() -> None:
    source_root = ROOT / "apps/fcp_0013_candidate_data_evidence_bundle_reconciliation_app_1"
    combined = ""
    for path in source_root.glob("*.py"):
        combined += path.read_text(encoding="ascii").lower()
    (ROOT / BUNDLE_REGISTRY).read_text(encoding="ascii")
    assert "import rqdatac" not in combined
    assert "import rqsdk" not in combined
    assert "requests." not in combined
    assert "urllib.request" not in combined
