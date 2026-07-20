from __future__ import annotations

import html
from dataclasses import dataclass
from typing import Tuple
from urllib.parse import parse_qs, urlsplit

from apps.browser_product_console_runtime_app_1 import (
    BrowserProductConsoleApplication,
    ConsoleReadModel,
    ConsoleResponse,
)

from .contracts import ConsoleLocale, LocalCSVPreview
from .localization import localize_html


_SECURITY_HEADERS = (
    ("Cache-Control", "no-store"),
    ("X-Content-Type-Options", "nosniff"),
    ("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'"),
)


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


@dataclass(frozen=True)
class LocalizedBrowserConsoleApplication:
    base_application: BrowserProductConsoleApplication
    default_locale: ConsoleLocale = ConsoleLocale()
    local_csv_previews: Tuple[LocalCSVPreview, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.base_application, BrowserProductConsoleApplication):
            raise TypeError("base_application must be BrowserProductConsoleApplication")
        if not isinstance(self.default_locale, ConsoleLocale):
            raise TypeError("default_locale must be ConsoleLocale")
        previews = tuple(self.local_csv_previews)
        if any(not isinstance(item, LocalCSVPreview) for item in previews):
            raise TypeError("local_csv_previews must contain LocalCSVPreview values")
        identities = tuple(item.artifact_id for item in previews)
        if len(identities) != len(set(identities)):
            raise ValueError("local CSV preview artifact IDs must be unique")
        object.__setattr__(self, "local_csv_previews", previews)

    @property
    def read_model(self) -> ConsoleReadModel:
        return self.base_application.read_model

    def _locale(self, raw_path: str) -> ConsoleLocale:
        values = parse_qs(urlsplit(raw_path).query, keep_blank_values=True).get("lang")
        if not values:
            return self.default_locale
        if len(values) != 1:
            raise ValueError("lang must appear at most once")
        return ConsoleLocale(values[0])

    @staticmethod
    def _language_control(locale: ConsoleLocale) -> str:
        other_id = "en" if locale.locale_id == "zh-CN" else "zh-CN"
        current = "Simplified Chinese" if locale.locale_id == "zh-CN" else "English"
        other = "English" if other_id == "en" else "Simplified Chinese"
        return (
            "<small>Presentation language: "
            f"<strong>{current}</strong> / "
            f'<a href="?lang={other_id}" style="color:#fff">{other}</a>'
            "</small>"
        )

    def _decorate(self, document: str, locale: ConsoleLocale) -> str:
        link = '<a class="" href="/local-data-intake">Local Data Intake</a>'
        if link not in document:
            document = document.replace("</nav>", f"{link}</nav>", 1)
        document = document.replace(
            "</header>",
            f"{self._language_control(locale)}</header>",
            1,
        )
        return localize_html(document, locale)

    def _intake_body(self) -> str:
        rows = []
        for preview in self.local_csv_previews:
            rows.append(
                "<tr>"
                f"<td>{_escape(preview.artifact_id)}</td>"
                f"<td>{_escape(preview.source_id)}</td>"
                f"<td>{preview.row_count}</td>"
                f"<td>{_escape(', '.join(preview.columns))}</td>"
                f"<td><code>{_escape(preview.source_artifact_sha256)}</code></td>"
                f"<td>{preview.repeated_bom_count}</td>"
                f"<td>{_escape(preview.rights_state)}</td>"
                f"<td>{_escape(preview.retention_state)}</td>"
                f"<td>{_escape(preview.product_evidence_state)}</td>"
                "</tr>"
            )
        if rows:
            preview_section = (
                '<section class="card">'
                "<h2>Registered local CSV previews</h2>"
                "<table><thead><tr>"
                "<th>Artifact ID</th><th>Source</th><th>Rows</th>"
                "<th>Columns</th><th>SHA-256</th>"
                "<th>BOM markers normalized in memory</th>"
                "<th>Rights state</th><th>Retention state</th>"
                "<th>Product evidence state</th>"
                "</tr></thead><tbody>"
                + "".join(rows)
                + "</tbody></table></section>"
            )
        else:
            preview_section = (
                '<section class="card">'
                "<h2>Registered local CSV previews</h2>"
                "<p>No registered local CSV preview</p>"
                "</section>"
            )
        return (
            '<section class="card">'
            "<h1>Local Data Intake Preview</h1>"
            "<p>State: <span class=\"state\">READ_ONLY_PREVIEW</span></p>"
            "</section>"
            + preview_section
            + '<section class="notice">'
            "<h2>Read-only intake guidance</h2>"
            "<p>Register exact byte length and SHA-256 before preview.</p>"
            "<p>Preview never copies, rewrites, uploads, or automatically registers source bytes.</p>"
            "<p>Commercial, retention, realtime, and provider decisions remain separate Operator gates.</p>"
            "</section>"
        )

    def dispatch(self, method: str, raw_path: str) -> ConsoleResponse:
        normalized_method = method.upper().strip()
        try:
            locale = self._locale(raw_path)
        except ValueError as exc:
            return ConsoleResponse(
                status=400,
                content_type="text/plain; charset=utf-8",
                body=str(exc).encode("utf-8") if normalized_method != "HEAD" else b"",
                headers=(("Cache-Control", "no-store"),),
            )
        path = urlsplit(raw_path).path or "/"
        if path == "/local-data-intake":
            if normalized_method not in {"GET", "HEAD"}:
                return ConsoleResponse(
                    status=405,
                    content_type="text/plain; charset=utf-8",
                    body=b"Method Not Allowed",
                    headers=(("Cache-Control", "no-store"),),
                )
            base = self.base_application.dispatch("GET", "/")
            document = base.body.decode("utf-8")
            start = document.index("<main>") + len("<main>")
            end = document.index("</main>")
            document = document[:start] + self._intake_body() + document[end:]
            document = self._decorate(document, locale)
            body = b"" if normalized_method == "HEAD" else document.encode("utf-8")
            return ConsoleResponse(
                status=200,
                content_type="text/html; charset=utf-8",
                body=body,
                headers=(*_SECURITY_HEADERS, ("Content-Language", locale.locale_id)),
            )
        response = self.base_application.dispatch(normalized_method, raw_path)
        if not response.content_type.startswith("text/html"):
            return response
        if not response.body:
            return ConsoleResponse(
                status=response.status,
                content_type=response.content_type,
                body=b"",
                headers=(*response.headers, ("Content-Language", locale.locale_id)),
            )
        document = self._decorate(response.body.decode("utf-8"), locale)
        return ConsoleResponse(
            status=response.status,
            content_type=response.content_type,
            body=document.encode("utf-8"),
            headers=(*response.headers, ("Content-Language", locale.locale_id)),
        )
