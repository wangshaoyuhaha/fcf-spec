import hashlib
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import MappingProxyType

import pytest

from apps.browser_product_console_runtime_app_1 import (
    BrowserProductConsoleApplication,
    ConsoleReadModel,
)
from apps.fcp_0008_chinese_browser_console_local_data_intake_preview_app_1 import (
    FCP_0008_BOUNDARY,
    ChineseConsoleLocalIntakeBoundary,
    ConsoleLocale,
    LocalCSVPreview,
    LocalizedBrowserConsoleApplication,
    RegisteredLocalCSVArtifact,
    inspect_registered_local_csv,
    localize_html,
)


def _model() -> ConsoleReadModel:
    return ConsoleReadModel(
        correlation_id="corr-fcp-0008-test",
        candidates=(),
        sections=MappingProxyType({}),
        source_artifact_ids=(),
    )


def _application(
    previews: tuple[LocalCSVPreview, ...] = (),
) -> LocalizedBrowserConsoleApplication:
    return LocalizedBrowserConsoleApplication(
        base_application=BrowserProductConsoleApplication(_model()),
        local_csv_previews=previews,
    )


def _csv_bytes() -> bytes:
    return (
        "symbol,date,close\n"
        "\ufeff000001.XSHE,2022-01-04,16.66\n"
        "\ufeff000001.XSHE,2022-01-05,17.15\n"
    ).encode("utf-8")


def _registration(payload: bytes, **updates: object) -> RegisteredLocalCSVArtifact:
    values = {
        "artifact_id": "local-csv-preview-1",
        "source_id": "operator-provided-local-csv",
        "artifact_sha256": hashlib.sha256(payload).hexdigest(),
        "byte_length": len(payload),
    }
    values.update(updates)
    return RegisteredLocalCSVArtifact(**values)  # type: ignore[arg-type]


def _preview(tmp_path: Path) -> LocalCSVPreview:
    payload = _csv_bytes()
    path = tmp_path / "sample.csv"
    path.write_bytes(payload)
    return inspect_registered_local_csv(path, _registration(payload))


def test_d1_boundary_is_closed_and_immutable() -> None:
    assert FCP_0008_BOUNDARY.paper_only is True
    assert FCP_0008_BOUNDARY.browser_upload_allowed is False
    assert FCP_0008_BOUNDARY.external_network_allowed is False
    with pytest.raises(FrozenInstanceError):
        FCP_0008_BOUNDARY.paper_only = False  # type: ignore[misc]


def test_d1_boundary_rejects_upload_or_realtime_authority() -> None:
    with pytest.raises(ValueError, match="cannot be weakened"):
        ChineseConsoleLocalIntakeBoundary(browser_upload_allowed=True)
    with pytest.raises(ValueError, match="cannot be weakened"):
        ChineseConsoleLocalIntakeBoundary(realtime_access_allowed=True)


def test_d2_locale_contract_is_explicit() -> None:
    assert ConsoleLocale().locale_id == "zh-CN"
    assert ConsoleLocale("en").locale_id == "en"
    with pytest.raises(ValueError, match="unsupported"):
        ConsoleLocale("zh")


def test_d2_localization_uses_ascii_source_and_unicode_output() -> None:
    document = '<html lang="en"><body>Overview</body></html>'
    localized = localize_html(document, ConsoleLocale("zh-CN"))
    assert 'lang="zh-CN"' in localized
    assert "\u603b\u89c8" in localized
    assert localize_html(document, ConsoleLocale("en")) == document


def test_d2_localization_preserves_registered_evidence_text() -> None:
    document = (
        '<html lang="en"><body><h1>Overview</h1>'
        '<td>Overview</td><code>English</code></body></html>'
    )
    localized = localize_html(document, ConsoleLocale("zh-CN"))
    assert "<h1>\u603b\u89c8</h1>" in localized
    assert "<td>Overview</td>" in localized
    assert "<code>English</code>" in localized


def test_d2_application_sources_are_ascii() -> None:
    root = Path(
        "apps/fcp_0008_chinese_browser_console_local_data_intake_preview_app_1"
    )
    for path in root.glob("*.py"):
        path.read_text(encoding="ascii")


def test_d3_preview_verifies_exact_source_and_normalizes_in_memory(
    tmp_path: Path,
) -> None:
    payload = _csv_bytes()
    path = tmp_path / "sample.csv"
    path.write_bytes(payload)
    result = inspect_registered_local_csv(path, _registration(payload))
    assert path.read_bytes() == payload
    assert result.row_count == 2
    assert result.columns == ("symbol", "date", "close")
    assert result.repeated_bom_count == 2
    assert result.source_artifact_sha256 == hashlib.sha256(payload).hexdigest()


def test_d3_preview_rejects_length_and_digest_mismatch(tmp_path: Path) -> None:
    payload = _csv_bytes()
    path = tmp_path / "sample.csv"
    path.write_bytes(payload)
    with pytest.raises(ValueError, match="byte length mismatch"):
        inspect_registered_local_csv(
            path,
            _registration(payload, byte_length=len(payload) + 1),
        )
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        inspect_registered_local_csv(
            path,
            _registration(payload, artifact_sha256="0" * 64),
        )


@pytest.mark.parametrize(
    ("payload", "message"),
    (
        (b"\xff\xfe", "must be UTF-8"),
        (b"a,a\n1,2\n", "columns must be unique"),
        (b"a,b\n1\n", "row width mismatch"),
        (b"a,b\n", "requires at least one data row"),
    ),
)
def test_d3_preview_rejects_invalid_csv(
    tmp_path: Path,
    payload: bytes,
    message: str,
) -> None:
    path = tmp_path / "invalid.csv"
    path.write_bytes(payload)
    with pytest.raises(ValueError, match=message):
        inspect_registered_local_csv(path, _registration(payload))


def test_d3_preview_mapping_is_immutable_and_product_blocked(
    tmp_path: Path,
) -> None:
    mapping = _preview(tmp_path).as_mapping()
    assert isinstance(mapping, MappingProxyType)
    assert mapping["product_evidence_state"] == "BLOCKED"
    assert mapping["provider_selected"] is False
    with pytest.raises(TypeError):
        mapping["provider_selected"] = True  # type: ignore[index]


def test_d4_existing_console_defaults_to_chinese() -> None:
    response = _application().dispatch("GET", "/")
    body = response.body.decode("utf-8")
    assert response.status == 200
    assert ("Content-Language", "zh-CN") in response.headers
    assert "\u603b\u89c8" in body
    assert "/local-data-intake" in body
    assert "<form" not in body and "<script" not in body


def test_d4_console_can_render_english_and_rejects_invalid_locale() -> None:
    english = _application().dispatch("GET", "/?lang=en")
    assert english.status == 200
    assert "Overview" in english.body.decode("utf-8")
    assert ("Content-Language", "en") in english.headers
    invalid = _application().dispatch("GET", "/?lang=unsafe")
    assert invalid.status == 400


def test_d4_local_intake_page_is_read_only_and_localized(tmp_path: Path) -> None:
    preview = _preview(tmp_path)
    response = _application((preview,)).dispatch("GET", "/local-data-intake")
    body = response.body.decode("utf-8")
    assert response.status == 200
    assert "local-csv-preview-1" in body
    assert hashlib.sha256(_csv_bytes()).hexdigest() in body
    assert "\u672c\u5730\u6570\u636e\u63a5\u5165\u9884\u68c0" in body
    assert "<form" not in body and "<button" not in body and "<script" not in body


def test_d5_head_and_write_methods_remain_fail_closed() -> None:
    head = _application().dispatch("HEAD", "/local-data-intake")
    assert head.status == 200
    assert head.body == b""
    assert ("Content-Language", "zh-CN") in head.headers
    post = _application().dispatch("POST", "/local-data-intake")
    assert post.status == 405
    assert post.body == b"Method Not Allowed"


def test_d5_existing_route_head_exposes_locale_without_body() -> None:
    response = _application().dispatch("HEAD", "/")
    assert response.status == 200
    assert response.body == b""
    assert ("Content-Language", "zh-CN") in response.headers


def test_d5_health_contract_is_not_localized_or_weakened() -> None:
    response = _application().dispatch("GET", "/health")
    body = response.body.decode("utf-8")
    assert response.status == 200
    assert response.content_type == "application/json; charset=utf-8"
    assert '"host_scope": "loopback-only"' in body
    assert '"operator_review_required": true' in body


def test_d6_preview_registration_cannot_claim_provider_or_rights() -> None:
    payload = _csv_bytes()
    with pytest.raises(ValueError, match="rights must remain unresolved"):
        _registration(payload, rights_state="APPROVED")
    with pytest.raises(ValueError, match="provider or storage authority"):
        _registration(payload, provider_selected=True)
    with pytest.raises(ValueError, match="byte_length"):
        _registration(payload, byte_length=1.5)
