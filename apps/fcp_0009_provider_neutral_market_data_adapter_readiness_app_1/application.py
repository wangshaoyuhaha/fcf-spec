from __future__ import annotations

import html
import re
from dataclasses import dataclass
from urllib.parse import parse_qs, urlsplit

from apps.browser_product_console_runtime_app_1 import ConsoleReadModel, ConsoleResponse
from apps.fcp_0008_chinese_browser_console_local_data_intake_preview_app_1 import (
    ConsoleLocale,
    LocalizedBrowserConsoleApplication,
    localize_html,
)

from .readiness import MarketDataAdapterReadinessSnapshot


_SECURITY_HEADERS = (
    ("Cache-Control", "no-store"),
    ("X-Content-Type-Options", "nosniff"),
    ("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'"),
)

_ZH_CN = {
    "Market Data Diagnostics": "\u5e02\u573a\u6570\u636e\u8bca\u65ad",
    "Local replay state": "\u672c\u5730\u56de\u653e\u72b6\u6001",
    "External activation state": "\u5916\u90e8\u6fc0\u6d3b\u72b6\u6001",
    "Provider selection": "\u6570\u636e\u4f9b\u5e94\u5546\u9009\u62e9",
    "Registered local replay health": "\u5df2\u767b\u8bb0\u672c\u5730\u56de\u653e\u5065\u5eb7\u5ea6",
    "Event count": "\u4e8b\u4ef6\u6570",
    "Stream count": "\u6570\u636e\u6d41\u6570",
    "Heartbeat age seconds": "\u5fc3\u8df3\u95f4\u9694\u79d2\u6570",
    "Maximum transport latency milliseconds": "\u6700\u5927\u4f20\u8f93\u5ef6\u8fdf\u6beb\u79d2",
    "Multi-clock state": "\u591a\u65f6\u949f\u72b6\u6001",
    "Degradation codes": "\u964d\u7ea7\u4ee3\u7801",
    "Canonical coverage": "\u6807\u51c6\u5b57\u6bb5\u8986\u76d6",
    "Observation kind": "\u89c2\u6d4b\u7c7b\u578b",
    "Mapping": "\u5b57\u6bb5\u6620\u5c04",
    "Observation": "\u89c2\u6d4b\u6570\u636e",
    "Closed activation gate": "\u5c01\u95ed\u6fc0\u6d3b\u95e8\u7981",
    "This page is read-only and uses registered local replay only.": (
        "\u672c\u9875\u9762\u4ec5\u4f9b\u67e5\u770b\uff0c\u4e14\u4ec5\u4f7f\u7528\u5df2\u767b\u8bb0\u7684\u672c\u5730\u56de\u653e\u6570\u636e\u3002"
    ),
    "Entitlement, retention, provider, credentials, and external network activation remain blocked.": (
        "\u6570\u636e\u6743\u5229\u3001\u4fdd\u7559\u6743\u3001\u4f9b\u5e94\u5546\u3001\u51ed\u636e\u548c\u5916\u7f51\u6fc0\u6d3b\u4ecd\u88ab\u7981\u6b62\u3002"
    ),
    "Operator review remains mandatory. No trading or execution path exists.": (
        "\u64cd\u4f5c\u5458\u590d\u6838\u4ecd\u4e3a\u5f3a\u5236\u8981\u6c42\uff0c\u7cfb\u7edf\u4e0d\u5b58\u5728\u4ea4\u6613\u6216\u6267\u884c\u8def\u5f84\u3002"
    ),
}


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


@dataclass(frozen=True)
class MarketDataDiagnosticsConsoleApplication:
    base_application: LocalizedBrowserConsoleApplication
    snapshot: MarketDataAdapterReadinessSnapshot

    def __post_init__(self) -> None:
        if not isinstance(self.base_application, LocalizedBrowserConsoleApplication):
            raise TypeError("base_application must be the FCP-0008 localized console")
        if not isinstance(self.snapshot, MarketDataAdapterReadinessSnapshot):
            raise TypeError("snapshot must be MarketDataAdapterReadinessSnapshot")

    @property
    def read_model(self) -> ConsoleReadModel:
        return self.base_application.read_model

    def _locale(self, raw_path: str) -> ConsoleLocale:
        values = parse_qs(urlsplit(raw_path).query, keep_blank_values=True).get("lang")
        if not values:
            return self.base_application.default_locale
        if len(values) != 1:
            raise ValueError("lang must appear at most once")
        return ConsoleLocale(values[0])

    @staticmethod
    def _nav(document: str) -> str:
        link = '<a class="" href="/market-data-diagnostics">Market Data Diagnostics</a>'
        if link not in document:
            document = document.replace("</nav>", f"{link}</nav>", 1)
        return document

    @staticmethod
    def _localize(document: str, locale: ConsoleLocale) -> str:
        localized = localize_html(document, locale)
        if locale.locale_id == "zh-CN":
            protected: list[str] = []

            def preserve(match: re.Match[str]) -> str:
                protected.append(match.group(0))
                return f"__FCF_FCP0009_LOCALIZATION_PROTECTED_{len(protected) - 1}__"

            localized = re.sub(
                r"<(?:code|td)\b[^>]*>.*?</(?:code|td)>",
                preserve,
                localized,
                flags=re.DOTALL | re.IGNORECASE,
            )
            for source in sorted(_ZH_CN, key=len, reverse=True):
                localized = localized.replace(source, _ZH_CN[source])
            for index, value in enumerate(protected):
                localized = localized.replace(
                    f"__FCF_FCP0009_LOCALIZATION_PROTECTED_{index}__",
                    value,
                )
        return localized

    def _body(self) -> str:
        snapshot = self.snapshot
        coverage = "".join(
            "<tr>"
            f"<td>{_escape(kind)}</td>"
            f"<td>{_escape(snapshot.mapping_coverage[kind])}</td>"
            f"<td>{_escape(snapshot.observation_coverage[kind])}</td>"
            "</tr>"
            for kind in snapshot.mapping_coverage
        )
        degradation = ", ".join(snapshot.degradation_codes) or "NONE"
        return (
            '<section class="card"><h1>Market Data Diagnostics</h1>'
            f'<p>Local replay state: <span class="state">{_escape(snapshot.local_replay_state)}</span></p>'
            f"<p>External activation state: {_escape(snapshot.external_activation_state)}</p>"
            f"<p>Provider selection: {_escape(snapshot.provider_selection_state)}</p>"
            "</section>"
            '<section class="card"><h2>Registered local replay health</h2>'
            "<table><tbody>"
            f"<tr><th>Event count</th><td>{snapshot.event_count}</td></tr>"
            f"<tr><th>Stream count</th><td>{snapshot.stream_count}</td></tr>"
            f"<tr><th>Heartbeat age seconds</th><td>{_escape(snapshot.heartbeat_age_seconds)}</td></tr>"
            f"<tr><th>Maximum transport latency milliseconds</th><td>{_escape(snapshot.max_transport_latency_ms)}</td></tr>"
            f"<tr><th>Multi-clock state</th><td>{_escape(snapshot.clock_state)}</td></tr>"
            f"<tr><th>Degradation codes</th><td>{_escape(degradation)}</td></tr>"
            "</tbody></table></section>"
            '<section class="card"><h2>Canonical coverage</h2>'
            "<table><thead><tr><th>Observation kind</th><th>Mapping</th><th>Observation</th></tr></thead>"
            f"<tbody>{coverage}</tbody></table></section>"
            '<section class="notice"><h2>Closed activation gate</h2>'
            "<p>This page is read-only and uses registered local replay only.</p>"
            "<p>Entitlement, retention, provider, credentials, and external network activation remain blocked.</p>"
            "<p>Operator review remains mandatory. No trading or execution path exists.</p>"
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
        if path == "/market-data-diagnostics":
            if normalized_method not in {"GET", "HEAD"}:
                return ConsoleResponse(
                    status=405,
                    content_type="text/plain; charset=utf-8",
                    body=b"Method Not Allowed",
                    headers=(("Cache-Control", "no-store"),),
                )
            base_path = "/?lang=" + locale.locale_id
            base = self.base_application.dispatch("GET", base_path)
            document = base.body.decode("utf-8")
            start = document.index("<main>") + len("<main>")
            end = document.index("</main>")
            document = document[:start] + self._body() + document[end:]
            document = self._localize(self._nav(document), locale)
            return ConsoleResponse(
                status=200,
                content_type="text/html; charset=utf-8",
                body=b"" if normalized_method == "HEAD" else document.encode("utf-8"),
                headers=(*_SECURITY_HEADERS, ("Content-Language", locale.locale_id)),
            )
        response = self.base_application.dispatch(normalized_method, raw_path)
        if not response.content_type.startswith("text/html") or not response.body:
            return response
        document = self._localize(self._nav(response.body.decode("utf-8")), locale)
        return ConsoleResponse(
            status=response.status,
            content_type=response.content_type,
            body=document.encode("utf-8"),
            headers=response.headers,
        )
