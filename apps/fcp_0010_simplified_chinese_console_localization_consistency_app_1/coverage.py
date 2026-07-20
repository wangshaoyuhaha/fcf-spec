from __future__ import annotations

import html
import re
from dataclasses import dataclass
from typing import Tuple

from .catalog import AUDITED_UI_LABELS


_IGNORED = re.compile(
    r"<(?:style|script|code|td)\b[^>]*>.*?</(?:style|script|code|td)>",
    flags=re.DOTALL | re.IGNORECASE,
)
_TAG = re.compile(r"<[^>]+>")


@dataclass(frozen=True)
class LocalizationCoverageReport:
    untranslated_labels: Tuple[str, ...]
    audited_label_count: int

    @property
    def complete(self) -> bool:
        return not self.untranslated_labels


def audit_simplified_chinese_document(document: str) -> LocalizationCoverageReport:
    if not isinstance(document, str):
        raise TypeError("document must be str")
    visible = html.unescape(_TAG.sub(" ", _IGNORED.sub(" ", document)))
    untranslated = tuple(
        label for label in AUDITED_UI_LABELS if label in visible
    )
    return LocalizationCoverageReport(
        untranslated_labels=untranslated,
        audited_label_count=len(AUDITED_UI_LABELS),
    )
