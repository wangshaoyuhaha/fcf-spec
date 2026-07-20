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
    AUDITED_UI_LABELS,
    FCP_0010_BOUNDARY,
    REGISTERED_HTML_ROUTES,
    ConsoleLocalizationConsistencyBoundary,
    SimplifiedChineseConsoleApplication,
    audit_simplified_chinese_document,
    localize_consistent_html,
)


def _application() -> SimplifiedChineseConsoleApplication:
    model = ConsoleReadModel(
        correlation_id="corr-fcp-0010-test",
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
    return SimplifiedChineseConsoleApplication(diagnostics)


def test_d1_boundary_is_closed_and_immutable() -> None:
    assert FCP_0010_BOUNDARY.presentation_only is True
    assert FCP_0010_BOUNDARY.preserves_registered_evidence is True
    assert FCP_0010_BOUNDARY.external_network_allowed is False
    with pytest.raises(FrozenInstanceError):
        FCP_0010_BOUNDARY.presentation_only = False  # type: ignore[misc]


@pytest.mark.parametrize(
    "update",
    (
        {"presentation_only": False},
        {"preserves_registered_evidence": False},
        {"preserves_deterministic_values": False},
        {"external_network_allowed": True},
        {"credentials_allowed": True},
        {"trading_or_execution_allowed": True},
    ),
)
def test_d1_boundary_rejects_added_authority(update: dict[str, bool]) -> None:
    with pytest.raises(ValueError, match="cannot"):
        replace(ConsoleLocalizationConsistencyBoundary(), **update)


def test_d2_catalog_is_bounded_and_ascii_source() -> None:
    assert len(AUDITED_UI_LABELS) >= 100
    assert len(REGISTERED_HTML_ROUTES) == 20
    root = Path(
        "apps/fcp_0010_simplified_chinese_console_localization_consistency_app_1"
    )
    for path in root.glob("*.py"):
        path.read_text(encoding="ascii")


def test_d3_localization_preserves_evidence_code_and_state_values() -> None:
    document = (
        '<html lang="en"><body><h1>Registered Artifacts</h1>'
        '<td>Registered Artifacts</td>'
        '<code>Operator Review Evidence</code>'
        '<span class="state">AVAILABLE</span></body></html>'
    )
    localized = localize_consistent_html(document, ConsoleLocale("zh-CN"))
    assert "\u5df2\u767b\u8bb0\u5de5\u4ef6" in localized
    assert "<td>Registered Artifacts</td>" in localized
    assert "<code>Operator Review Evidence</code>" in localized
    assert '<span class="state">AVAILABLE</span>' in localized


def test_d3_english_document_is_byte_for_byte_unchanged() -> None:
    document = '<html lang="en"><h1>Evidence Overview</h1></html>'
    assert localize_consistent_html(document, ConsoleLocale("en")) == document


@pytest.mark.parametrize("path", REGISTERED_HTML_ROUTES)
def test_d4_every_registered_route_is_consistently_chinese(path: str) -> None:
    response = _application().dispatch("GET", path)
    body = response.body.decode("utf-8")
    report = audit_simplified_chinese_document(body)
    assert response.status == 200
    assert ("Content-Language", "zh-CN") in response.headers
    assert report.complete, (path, report.untranslated_labels)
    assert "<form" not in body and "<button" not in body and "<script" not in body


def test_d4_reported_navigation_is_fully_chinese() -> None:
    body = _application().dispatch("GET", "/evidence").body.decode("utf-8")
    for source in (
        "Evidence Overview",
        "Registered Artifacts",
        "Correlation Lineage",
        "Risk and Contradictions",
        "Validation Evidence",
        "Operator Review Evidence",
        "Archive Evidence",
    ):
        assert f">{source}<" not in body
    assert "\u8bc1\u636e\u603b\u89c8" in body
    assert "\u64cd\u4f5c\u5458\u590d\u6838\u8bc1\u636e" in body


def test_d5_explicit_english_preserves_filters_and_navigation() -> None:
    response = _application().dispatch("GET", "/evidence?limit=1&lang=en")
    body = response.body.decode("utf-8")
    assert response.status == 200
    assert ("Content-Language", "en") in response.headers
    assert "Evidence Overview" in body
    assert "Registered Artifacts" in body
    assert "limit" in body


@pytest.mark.parametrize("path", REGISTERED_HTML_ROUTES)
def test_d5_head_matches_get_status_without_body(path: str) -> None:
    response = _application().dispatch("HEAD", path)
    assert response.status == 200
    assert response.body == b""
    assert ("Content-Language", "zh-CN") in response.headers


@pytest.mark.parametrize("method", ("POST", "PUT", "PATCH", "DELETE"))
def test_d5_write_methods_remain_rejected(method: str) -> None:
    response = _application().dispatch(method, "/evidence")
    assert response.status == 405


def test_d5_duplicate_or_invalid_locale_is_rejected() -> None:
    duplicate = _application().dispatch("GET", "/?lang=en&lang=zh-CN")
    invalid = _application().dispatch("GET", "/?lang=unsafe")
    assert duplicate.status == 400
    assert invalid.status == 400


def test_d6_health_contract_remains_untranslated_and_closed() -> None:
    response = _application().dispatch("GET", "/health?lang=zh-CN")
    body = response.body.decode("utf-8")
    assert response.status == 200
    assert response.content_type == "application/json; charset=utf-8"
    assert '"host_scope": "loopback-only"' in body
    assert '"operator_review_required": true' in body
