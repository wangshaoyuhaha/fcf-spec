from __future__ import annotations

import html
import re
from dataclasses import dataclass
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from apps.browser_product_console_runtime_app_1 import ConsoleReadModel, ConsoleResponse
from apps.fcp_0008_chinese_browser_console_local_data_intake_preview_app_1 import (
    ConsoleLocale,
)
from apps.fcp_0009_provider_neutral_market_data_adapter_readiness_app_1 import (
    MarketDataDiagnosticsConsoleApplication,
)

from .localization import localize_consistent_html


_LANGUAGE_CONTROL = re.compile(
    r"<small>Presentation language:.*?</small>",
    flags=re.DOTALL | re.IGNORECASE,
)


@dataclass(frozen=True)
class SimplifiedChineseConsoleApplication:
    base_application: MarketDataDiagnosticsConsoleApplication
    default_locale: ConsoleLocale = ConsoleLocale("zh-CN")

    def __post_init__(self) -> None:
        if not isinstance(
            self.base_application,
            MarketDataDiagnosticsConsoleApplication,
        ):
            raise TypeError("base_application must be the FCP-0009 console")
        if not isinstance(self.default_locale, ConsoleLocale):
            raise TypeError("default_locale must be ConsoleLocale")

    @property
    def read_model(self) -> ConsoleReadModel:
        return self.base_application.read_model

    def _request(self, raw_path: str) -> tuple[ConsoleLocale, str]:
        parts = urlsplit(raw_path)
        pairs = parse_qsl(parts.query, keep_blank_values=True)
        values = [value for name, value in pairs if name == "lang"]
        if len(values) > 1:
            raise ValueError("lang must appear at most once")
        locale = self.default_locale if not values else ConsoleLocale(values[0])
        base_query = urlencode(
            [(name, value) for name, value in pairs if name != "lang"],
            doseq=True,
        )
        base_path = urlunsplit(("", "", parts.path or "/", base_query, ""))
        return locale, base_path

    @staticmethod
    def _language_control(locale: ConsoleLocale, raw_path: str) -> str:
        parts = urlsplit(raw_path)
        pairs = [
            (name, value)
            for name, value in parse_qsl(parts.query, keep_blank_values=True)
            if name != "lang"
        ]
        other_id = "en" if locale.locale_id == "zh-CN" else "zh-CN"
        pairs.append(("lang", other_id))
        link = urlunsplit(("", "", parts.path or "/", urlencode(pairs), ""))
        current = "Simplified Chinese" if locale.locale_id == "zh-CN" else "English"
        other = "English" if other_id == "en" else "Simplified Chinese"
        return (
            "<small>Presentation language: "
            f"<strong>{current}</strong> / "
            f'<a href="{html.escape(link, quote=True)}" style="color:#fff">{other}</a>'
            "</small>"
        )

    def _decorate(
        self,
        document: str,
        locale: ConsoleLocale,
        raw_path: str,
    ) -> str:
        control = self._language_control(locale, raw_path)
        if _LANGUAGE_CONTROL.search(document):
            document = _LANGUAGE_CONTROL.sub(control, document, count=1)
        else:
            document = document.replace("</header>", f"{control}</header>", 1)
        return localize_consistent_html(document, locale)

    def dispatch(self, method: str, raw_path: str) -> ConsoleResponse:
        normalized_method = method.upper().strip()
        try:
            locale, base_path = self._request(raw_path)
        except ValueError as exc:
            return ConsoleResponse(
                status=400,
                content_type="text/plain; charset=utf-8",
                body=str(exc).encode("utf-8") if normalized_method != "HEAD" else b"",
                headers=(("Cache-Control", "no-store"),),
            )

        response = self.base_application.dispatch(normalized_method, base_path)
        headers = tuple(
            (name, value)
            for name, value in response.headers
            if name.lower() != "content-language"
        )
        if not response.content_type.startswith("text/html"):
            return ConsoleResponse(
                status=response.status,
                content_type=response.content_type,
                body=response.body,
                headers=headers,
            )
        body = response.body
        if body:
            body = self._decorate(
                body.decode("utf-8"),
                locale,
                raw_path,
            ).encode("utf-8")
        return ConsoleResponse(
            status=response.status,
            content_type=response.content_type,
            body=body,
            headers=(*headers, ("Content-Language", locale.locale_id)),
        )
