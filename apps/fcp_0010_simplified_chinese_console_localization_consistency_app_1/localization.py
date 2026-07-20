from __future__ import annotations

import re

from apps.fcp_0008_chinese_browser_console_local_data_intake_preview_app_1 import (
    ConsoleLocale,
)

from .catalog import ZH_CN_CONSOLE_TRANSLATIONS


_PROTECTED_ELEMENT = re.compile(
    r"<(?:code|td)\b[^>]*>.*?</(?:code|td)>",
    flags=re.DOTALL | re.IGNORECASE,
)


def localize_consistent_html(document: str, locale: ConsoleLocale) -> str:
    if not isinstance(document, str):
        raise TypeError("document must be str")
    if not isinstance(locale, ConsoleLocale):
        raise TypeError("locale must be ConsoleLocale")
    if locale.locale_id == "en":
        return document

    localized = document.replace('lang="en"', 'lang="zh-CN"')
    protected: list[str] = []

    def preserve(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return f"__FCF_FCP0010_PROTECTED_{len(protected) - 1}__"

    localized = _PROTECTED_ELEMENT.sub(preserve, localized)
    for source in sorted(ZH_CN_CONSOLE_TRANSLATIONS, key=len, reverse=True):
        localized = localized.replace(source, ZH_CN_CONSOLE_TRANSLATIONS[source])
    for index, value in enumerate(protected):
        localized = localized.replace(f"__FCF_FCP0010_PROTECTED_{index}__", value)
    return localized
