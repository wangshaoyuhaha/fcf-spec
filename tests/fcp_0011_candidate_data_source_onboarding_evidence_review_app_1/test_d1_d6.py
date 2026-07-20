from dataclasses import FrozenInstanceError, replace
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
    EVIDENCE_CATEGORIES,
    FCP_0011_BOUNDARY,
    AccessApplicationState,
    CandidateDataSourceOnboardingApplication,
    CandidateDataSourceOnboardingBoundary,
    CandidateSourceProfile,
    build_complete_synthetic_candidate,
    build_operator_declared_candidate_profiles,
    required_canonical_fields,
    review_candidate_source,
    review_candidate_sources,
)
from scripts.run_fcp_0011_candidate_data_source_onboarding import main


def _application() -> CandidateDataSourceOnboardingApplication:
    model = ConsoleReadModel(
        correlation_id="corr-fcp-0011-test",
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
    return CandidateDataSourceOnboardingApplication(
        chinese,
        build_operator_declared_candidate_profiles(),
    )


def test_d1_boundary_is_closed_and_immutable() -> None:
    assert FCP_0011_BOUNDARY.external_network_allowed is False
    assert FCP_0011_BOUNDARY.credentials_allowed is False
    assert FCP_0011_BOUNDARY.provider_selection_allowed is False
    assert FCP_0011_BOUNDARY.operator_review_required is True
    with pytest.raises(FrozenInstanceError):
        FCP_0011_BOUNDARY.local_only = False  # type: ignore[misc]


@pytest.mark.parametrize(
    "update",
    (
        {"external_network_allowed": True},
        {"credentials_allowed": True},
        {"provider_selection_allowed": True},
        {"entitlement_approval_allowed": True},
        {"realtime_activation_allowed": True},
        {"trading_or_execution_allowed": True},
        {"operator_review_required": False},
    ),
)
def test_d1_boundary_rejects_added_authority(update: dict[str, bool]) -> None:
    with pytest.raises(ValueError, match="cannot"):
        replace(CandidateDataSourceOnboardingBoundary(), **update)


def test_d1_profile_rejects_secret_material_and_activation_claims() -> None:
    with pytest.raises(ValueError, match="secret"):
        CandidateSourceProfile("candidate-a", "A", secret_material_present=True)
    with pytest.raises(ValueError, match="select"):
        CandidateSourceProfile(
            "candidate-a", "A", provider_selection_state="SELECTED"
        )
    with pytest.raises(ValueError, match="network"):
        CandidateSourceProfile("candidate-a", "A", network_state="ENABLED")


def test_d1_profile_collections_are_immutable_and_normalized() -> None:
    profile = CandidateSourceProfile(
        "candidate-a",
        "Candidate A",
        declared_market_ids=("market-b", "market-a", "market-a"),
        declared_canonical_fields={"TICK": ("volume", "last")},
        evidence_by_category={"rights": ("evidence-b", "evidence-a")},
    )
    assert profile.declared_market_ids == ("market-a", "market-b")
    assert isinstance(profile.declared_canonical_fields, MappingProxyType)
    assert isinstance(profile.evidence_by_category, MappingProxyType)
    with pytest.raises(TypeError):
        profile.declared_canonical_fields["TICK"] = ()  # type: ignore[index]


def test_d2_evidence_categories_are_closed() -> None:
    assert len(EVIDENCE_CATEGORIES) == 8
    with pytest.raises(ValueError, match="category"):
        CandidateSourceProfile(
            "candidate-a",
            "A",
            evidence_by_category={"unregistered-category": ("evidence-a",)},
        )


def test_d3_required_fields_reuse_fcp_0009_closed_schemas() -> None:
    required = required_canonical_fields()
    assert tuple(required) == ("TICK", "MINUTE_BAR", "ORDER_BOOK")
    assert required["TICK"] == ("instrument_id", "event_at", "last", "volume")
    assert isinstance(required, MappingProxyType)


def test_d3_unknown_observation_kind_is_rejected() -> None:
    with pytest.raises(ValueError, match="canonical"):
        CandidateSourceProfile(
            "candidate-a",
            "A",
            declared_canonical_fields={"VENDOR_PRIVATE_KIND": ("field-a",)},
        )


def test_d4_operator_declared_candidates_remain_incomplete_and_blocked() -> None:
    profiles = build_operator_declared_candidate_profiles()
    packets = review_candidate_sources(profiles)
    assert tuple(profile.candidate_id for profile in profiles) == (
        "candidate-akshare",
        "candidate-baostock",
        "candidate-guojin-qmt",
        "candidate-rqdata",
        "candidate-tushare",
    )
    assert all(packet.documentary_status == "INCOMPLETE" for packet in packets)
    assert all(packet.compatibility_status == "INCOMPLETE" for packet in packets)
    assert all(packet.external_activation_state == "BLOCKED" for packet in packets)
    assert all(packet.credential_state == "ABSENT" for packet in packets)


def test_d4_complete_synthetic_candidate_still_cannot_activate() -> None:
    packet = review_candidate_source(build_complete_synthetic_candidate())
    assert packet.documentary_status == "COMPLETE_PENDING_OPERATOR_REVIEW"
    assert packet.compatibility_status == "COMPLETE"
    assert packet.external_activation_state == "BLOCKED"
    assert packet.entitlement_state == "UNRESOLVED"
    assert packet.provider_selection_state == "UNSELECTED"
    assert len(packet.packet_hash) == 64


def test_d4_review_is_deterministic_and_mapping_payload_is_immutable() -> None:
    profile = build_complete_synthetic_candidate()
    first = review_candidate_source(profile)
    second = review_candidate_source(profile)
    assert first == second
    assert first.packet_hash == second.packet_hash
    payload = first.as_payload()
    assert isinstance(payload, MappingProxyType)
    with pytest.raises(TypeError):
        payload["network_state"] = "ENABLED"  # type: ignore[index]


def test_d4_missing_field_and_evidence_remain_explicit() -> None:
    profile = CandidateSourceProfile(
        "candidate-a",
        "A",
        access_application_state=AccessApplicationState.PENDING,
        declared_canonical_fields={"TICK": ("instrument_id", "event_at")},
        evidence_by_category={"rights": ("evidence-rights",)},
    )
    packet = review_candidate_source(profile)
    assert "permitted-use" in packet.missing_evidence_categories
    assert packet.missing_fields_by_kind["TICK"] == ("last", "volume")
    assert set(packet.missing_fields_by_kind) == {
        "TICK",
        "MINUTE_BAR",
        "ORDER_BOOK",
    }


def test_d4_duplicate_candidate_identity_is_rejected() -> None:
    profile = CandidateSourceProfile("candidate-a", "A")
    with pytest.raises(ValueError, match="unique"):
        review_candidate_sources((profile, profile))


def test_d5_chinese_review_is_default_and_contains_no_controls() -> None:
    response = _application().dispatch("GET", "/data-source-onboarding")
    body = response.body.decode("ascii")
    assert response.status == 200
    assert ("Content-Language", "zh-CN") in response.headers
    assert "&#20505;" in body
    assert "candidate-guojin-qmt" not in body
    assert "Guojin QMT" in body
    assert "<form" not in body and "<button" not in body and "<script" not in body


def test_d5_explicit_english_review_preserves_authoritative_values() -> None:
    response = _application().dispatch("GET", "/data-source-onboarding?lang=en")
    body = response.body.decode("ascii")
    assert response.status == 200
    assert ("Content-Language", "en") in response.headers
    assert "Candidate Data Source Onboarding Review" in body
    assert "INCOMPLETE" in body and "BLOCKED" in body


def test_d5_head_has_no_body_and_write_methods_are_rejected() -> None:
    head = _application().dispatch("HEAD", "/data-source-onboarding")
    post = _application().dispatch("POST", "/data-source-onboarding")
    assert head.status == 200 and head.body == b""
    assert post.status == 405
    assert ("Allow", "GET, HEAD") in post.headers


@pytest.mark.parametrize(
    "path",
    (
        "/data-source-onboarding?lang=unsafe",
        "/data-source-onboarding?lang=en&lang=zh-CN",
    ),
)
def test_d5_invalid_locale_is_rejected(path: str) -> None:
    assert _application().dispatch("GET", path).status == 400


def test_d5_existing_health_route_is_delegated_unchanged() -> None:
    response = _application().dispatch("GET", "/health?lang=zh-CN")
    assert response.status == 200
    assert response.content_type == "application/json; charset=utf-8"


def test_d6_local_json_review_is_non_networked(capsys) -> None:
    assert main(["--review-json"]) == 0
    output = capsys.readouterr().out
    assert '"external_activation_state": "BLOCKED"' in output
    assert '"credential_state": "ABSENT"' in output
    assert "http://" not in output and "https://" not in output


def test_d6_app_sources_are_ascii() -> None:
    from pathlib import Path

    root = Path("apps/fcp_0011_candidate_data_source_onboarding_evidence_review_app_1")
    for path in root.glob("*.py"):
        path.read_text(encoding="ascii")
