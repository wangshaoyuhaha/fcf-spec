import hashlib
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
    CandidateSourceProfile,
    build_operator_declared_candidate_profiles,
)
from apps.fcp_0012_sanitized_candidate_data_session_evidence_intake_app_1 import (
    FCP_0012_BOUNDARY,
    CandidateSessionEvidence,
    ReadOnlyProbeEvidence,
    RegisteredSessionEvidenceArtifact,
    SanitizedSessionEvidenceApplication,
    SanitizedSessionEvidenceBoundary,
    build_rqdata_trial_registration,
    load_registered_session_evidence,
    load_rqdata_trial_session,
    review_candidate_session_evidence,
)
from scripts.run_fcp_0012_sanitized_session_evidence import main


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_NAME = "FCF_LOCAL_ARTIFACT_FCP_0012_RQDATA_TRIAL_SESSION.json"


def _registration(raw: bytes) -> RegisteredSessionEvidenceArtifact:
    return RegisteredSessionEvidenceArtifact(
        artifact_id="artifact-test-v1",
        artifact_path=ARTIFACT_NAME,
        artifact_sha256=hashlib.sha256(raw).hexdigest(),
        byte_length=len(raw),
        candidate_id="candidate-rqdata",
        evidence_id="evidence-test-v1",
    )


def _write(tmp_path: Path, raw: bytes) -> Path:
    path = tmp_path / ARTIFACT_NAME
    path.write_bytes(raw)
    return path


def _application() -> SanitizedSessionEvidenceApplication:
    model = ConsoleReadModel(
        correlation_id="corr-fcp-0012-test",
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
    return SanitizedSessionEvidenceApplication(
        onboarding,
        profile,
        registration,
        evidence,
    )


def test_d1_boundary_is_closed_and_immutable() -> None:
    assert FCP_0012_BOUNDARY.external_network_allowed is False
    assert FCP_0012_BOUNDARY.credentials_allowed is False
    assert FCP_0012_BOUNDARY.raw_market_values_allowed is False
    assert FCP_0012_BOUNDARY.provider_selection_allowed is False
    with pytest.raises(FrozenInstanceError):
        FCP_0012_BOUNDARY.local_only = False  # type: ignore[misc]


@pytest.mark.parametrize(
    "update",
    (
        {"external_network_allowed": True},
        {"credentials_allowed": True},
        {"raw_market_values_allowed": True},
        {"provider_selection_allowed": True},
        {"entitlement_approval_allowed": True},
        {"realtime_activation_allowed": True},
        {"trading_or_execution_allowed": True},
        {"operator_review_required": False},
    ),
)
def test_d1_boundary_rejects_added_authority(update: dict[str, bool]) -> None:
    with pytest.raises(ValueError, match="cannot"):
        replace(SanitizedSessionEvidenceBoundary(), **update)


def test_d1_registration_rejects_credentials_and_provider_selection() -> None:
    raw = b"{}"
    with pytest.raises(ValueError, match="cannot"):
        replace(_registration(raw), credentials_committed=True)
    with pytest.raises(ValueError, match="cannot"):
        replace(_registration(raw), provider_selected=True)


def test_d2_registered_repository_artifact_loads_exactly() -> None:
    profile, registration, evidence = load_rqdata_trial_session(ROOT)
    assert profile.candidate_id == "candidate-rqdata"
    assert registration.byte_length == 383
    assert evidence.license_class == "TRIAL"
    assert evidence.remaining_days == 29
    assert evidence.quota_limit_bytes == 1073741824
    assert evidence.probe.kind == "DAILY_BAR"
    assert evidence.probe.row_count == 3


def test_d2_registry_digest_matches_exact_artifact() -> None:
    registration = build_rqdata_trial_registration(ROOT)
    raw = (ROOT / registration.artifact_path).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == registration.artifact_sha256
    assert len(raw) == registration.byte_length


def test_d2_tampered_artifact_is_rejected(tmp_path: Path) -> None:
    registration = build_rqdata_trial_registration(ROOT)
    path = _write(tmp_path, (ROOT / registration.artifact_path).read_bytes() + b" ")
    with pytest.raises(ValueError, match="length"):
        load_registered_session_evidence(path, registration)


def test_d2_duplicate_json_key_is_rejected(tmp_path: Path) -> None:
    raw = b'{"candidate_id":"candidate-rqdata","candidate_id":"candidate-rqdata"}'
    with pytest.raises(ValueError, match="duplicate"):
        load_registered_session_evidence(_write(tmp_path, raw), _registration(raw))


def test_d2_forbidden_nested_secret_key_is_rejected(tmp_path: Path) -> None:
    raw = (
        b'{"candidate_id":"candidate-rqdata","captured_at_utc":"2026-07-20T12:55:47Z",'
        b'"license_class":"TRIAL","probe":{"first_date":"2026-07-15","instrument_count":1,'
        b'"kind":"DAILY_BAR","last_date":"2026-07-17","row_count":3,"status":"SUCCEEDED",'
        b'"access_token":"forbidden"},"quota_limit_bytes":10,"quota_used_bytes":1,"remaining_days":1}'
    )
    with pytest.raises(ValueError, match="forbidden"):
        load_registered_session_evidence(_write(tmp_path, raw), _registration(raw))


def test_d3_probe_contract_rejects_reversed_dates_and_empty_success() -> None:
    with pytest.raises(ValueError, match="reversed"):
        ReadOnlyProbeEvidence("DAILY_BAR", "SUCCEEDED", 1, 1, "2026-07-17", "2026-07-15")
    with pytest.raises(ValueError, match="requires"):
        ReadOnlyProbeEvidence("DAILY_BAR", "SUCCEEDED", 1, 0, None, None)


def test_d3_evidence_collections_and_payload_are_immutable() -> None:
    profile, registration, evidence = load_rqdata_trial_session(ROOT)
    packet = review_candidate_session_evidence(profile, registration, evidence)
    assert isinstance(packet.missing_fields_by_kind, MappingProxyType)
    assert isinstance(packet.as_payload(), MappingProxyType)
    with pytest.raises(TypeError):
        packet.as_payload()["network_state"] = "ENABLED"  # type: ignore[index]


def test_d4_session_observation_does_not_close_documentary_or_field_gaps() -> None:
    profile, registration, evidence = load_rqdata_trial_session(ROOT)
    packet = review_candidate_session_evidence(profile, registration, evidence)
    assert packet.operational_observation_status == "OBSERVED_READ_ONLY_PROBE"
    assert packet.documentary_status == "INCOMPLETE"
    assert packet.compatibility_status == "INCOMPLETE"
    assert set(packet.missing_fields_by_kind) == {"TICK", "MINUTE_BAR", "ORDER_BOOK"}
    assert "rights" in packet.missing_evidence_categories
    assert packet.external_activation_state == "BLOCKED"
    assert packet.entitlement_state == "UNRESOLVED"
    assert packet.provider_selection_state == "UNSELECTED"


def test_d4_review_is_deterministic() -> None:
    profile, registration, evidence = load_rqdata_trial_session(ROOT)
    first = review_candidate_session_evidence(profile, registration, evidence)
    second = review_candidate_session_evidence(profile, registration, evidence)
    assert first == second
    assert len(first.packet_hash) == 64


def test_d4_candidate_identity_mismatch_is_rejected() -> None:
    _, registration, evidence = load_rqdata_trial_session(ROOT)
    with pytest.raises(ValueError, match="identities"):
        review_candidate_session_evidence(
            CandidateSourceProfile("candidate-other", "Other"),
            registration,
            evidence,
        )


def test_d5_chinese_page_is_default_and_has_no_controls_or_secrets() -> None:
    response = _application().dispatch("GET", "/data-source-session-evidence")
    body = response.body.decode("ascii")
    assert response.status == 200
    assert ("Content-Language", "zh-CN") in response.headers
    assert "&#20505;" in body
    assert "TRIAL" in body and "BLOCKED" in body
    assert "000001.XSHE" not in body
    assert "<form" not in body and "<button" not in body and "<script" not in body
    assert "token" not in body.lower() and "password" not in body.lower()


def test_d5_english_head_write_and_delegation_contracts() -> None:
    app = _application()
    english = app.dispatch("GET", "/data-source-session-evidence?lang=en")
    head = app.dispatch("HEAD", "/data-source-session-evidence")
    post = app.dispatch("POST", "/data-source-session-evidence")
    health = app.dispatch("GET", "/health?lang=zh-CN")
    assert english.status == 200 and b"Candidate Session Evidence Review" in english.body
    assert head.status == 200 and head.body == b""
    assert post.status == 405 and ("Allow", "GET, HEAD") in post.headers
    assert health.status == 200


@pytest.mark.parametrize(
    "path",
    (
        "/data-source-session-evidence?lang=unsafe",
        "/data-source-session-evidence?lang=en&lang=zh-CN",
    ),
)
def test_d5_invalid_locale_is_rejected(path: str) -> None:
    assert _application().dispatch("GET", path).status == 400


def test_d6_local_review_json_is_safe_and_non_networked(capsys) -> None:
    assert main(["--review-json"]) == 0
    output = capsys.readouterr().out
    assert '"external_activation_state": "BLOCKED"' in output
    assert '"credential_state": "ABSENT"' in output
    assert "000001.XSHE" not in output
    assert "http://" not in output and "https://" not in output


def test_d6_startup_preflight_passes_on_free_port() -> None:
    assert main(["--check", "--port", "18765", "--no-browser"]) == 0


def test_d6_sources_and_registered_json_are_ascii() -> None:
    for path in Path("apps/fcp_0012_sanitized_candidate_data_session_evidence_intake_app_1").glob("*.py"):
        path.read_text(encoding="ascii")
    (ROOT / ARTIFACT_NAME).read_text(encoding="ascii")
    (ROOT / "FCF_REGISTERED_EVIDENCE_FCP_0012_RQDATA_TRIAL_SESSION.json").read_text(encoding="ascii")
