from __future__ import annotations

import html
from dataclasses import dataclass
from urllib.parse import parse_qsl, urlsplit

from apps.browser_product_console_runtime_app_1 import ConsoleResponse
from apps.fcp_0010_simplified_chinese_console_localization_consistency_app_1 import (
    SimplifiedChineseConsoleApplication,
)

from .contracts import CandidateSourceProfile, CandidateSourceReviewPacket
from .review import review_candidate_sources


ROUTE = "/data-source-onboarding"


def _zh(value: str) -> str:
    return "".join(f"&#{ord(char)};" if ord(char) > 127 else char for char in value)


ZH = {
    "title": _zh("\u5019\u9009\u6570\u636e\u6e90\u63a5\u5165\u5ba1\u67e5"),
    "candidate": _zh("\u5019\u9009\u6570\u636e\u6e90"),
    "application": _zh("\u7533\u8bf7\u72b6\u6001"),
    "documents": _zh("\u8d44\u6599\u5b8c\u6574\u5ea6"),
    "fields": _zh("\u5b57\u6bb5\u517c\u5bb9\u5ea6"),
    "missing_documents": _zh("\u7f3a\u5c11\u8d44\u6599"),
    "missing_fields": _zh("\u7f3a\u5c11\u5b57\u6bb5"),
    "activation": _zh("\u5916\u90e8\u6fc0\u6d3b"),
    "notice": _zh(
        "\u672c\u9875\u4ec5\u5c55\u793a\u64cd\u4f5c\u5458\u58f0\u660e\u548c\u5df2\u767b\u8bb0\u8bc1\u636e\u3002"
        "\u7cfb\u7edf\u4e0d\u4f1a\u9009\u62e9\u4f9b\u5e94\u5546\u3001\u63a5\u6536\u5bc6\u94a5\u3001"
        "\u8054\u7f51\u6216\u6279\u51c6\u6570\u636e\u6743\u5229\u3002"
    ),
    "back": _zh("\u8fd4\u56de\u603b\u89c8"),
    "language": _zh("\u663e\u793a\u8bed\u8a00"),
    "none": _zh("\u65e0"),
}


@dataclass(frozen=True)
class CandidateDataSourceOnboardingApplication:
    base_application: SimplifiedChineseConsoleApplication
    profiles: tuple[CandidateSourceProfile, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.base_application, SimplifiedChineseConsoleApplication):
            raise TypeError("base_application must be the FCP-0010 console")
        profiles = tuple(self.profiles)
        review_candidate_sources(profiles)
        object.__setattr__(self, "profiles", profiles)

    @property
    def read_model(self):
        return self.base_application.read_model

    @staticmethod
    def _locale(raw_path: str) -> str:
        values = [
            value
            for name, value in parse_qsl(urlsplit(raw_path).query, keep_blank_values=True)
            if name == "lang"
        ]
        if len(values) > 1 or (values and values[0] not in {"zh-CN", "en"}):
            raise ValueError("lang must be zh-CN or en and appear at most once")
        return values[0] if values else "zh-CN"

    def _document(self, locale: str) -> str:
        reviews = review_candidate_sources(self.profiles)
        profiles = {profile.candidate_id: profile for profile in self.profiles}
        labels = ZH if locale == "zh-CN" else {
            "title": "Candidate Data Source Onboarding Review",
            "candidate": "Candidate",
            "application": "Application state",
            "documents": "Documentary status",
            "fields": "Field compatibility",
            "missing_documents": "Missing evidence",
            "missing_fields": "Missing fields",
            "activation": "External activation",
            "notice": (
                "This page presents Operator declarations and registered evidence only. "
                "It cannot select a provider, accept secrets, connect a network, or approve data rights."
            ),
            "back": "Back to overview",
            "language": "Presentation language",
            "none": "None",
        }
        other = "en" if locale == "zh-CN" else "zh-CN"
        rows = "".join(self._row(review, profiles[review.candidate_id], labels) for review in reviews)
        return (
            "<!doctype html><html><head><meta charset=\"utf-8\">"
            f"<title>{labels['title']}</title>"
            "<style>body{font-family:Arial,sans-serif;margin:0;background:#f3f0e8;color:#10222b}"
            "header{background:#0d3038;color:#fff;padding:20px}main{padding:24px}"
            "table{border-collapse:collapse;width:100%;background:#fff}th,td{border:1px solid #ddd;padding:10px;vertical-align:top}"
            "th{background:#e8eef0;text-align:left}.notice{border-left:4px solid #c56d35;background:#fff7eb;padding:12px;margin:16px 0}"
            "code{white-space:normal;word-break:break-word}</style></head><body>"
            f"<header><h1>{labels['title']}</h1>"
            f"<small>{labels['language']}: <strong>{html.escape(locale)}</strong> / "
            f"<a style=\"color:#fff\" href=\"{ROUTE}?lang={other}\">{other}</a></small></header>"
            f"<main><p><a href=\"/?lang={locale}\">{labels['back']}</a></p>"
            f"<div class=\"notice\">{labels['notice']}</div><table><thead><tr>"
            f"<th>{labels['candidate']}</th><th>{labels['application']}</th>"
            f"<th>{labels['documents']}</th><th>{labels['fields']}</th>"
            f"<th>{labels['missing_documents']}</th><th>{labels['missing_fields']}</th>"
            f"<th>{labels['activation']}</th></tr></thead><tbody>{rows}</tbody></table></main></body></html>"
        )

    @staticmethod
    def _row(
        review: CandidateSourceReviewPacket,
        profile: CandidateSourceProfile,
        labels: dict[str, str],
    ) -> str:
        missing_documents = ", ".join(review.missing_evidence_categories) or labels["none"]
        missing_fields = "; ".join(
            f"{kind}: {', '.join(fields)}"
            for kind, fields in review.missing_fields_by_kind.items()
        ) or labels["none"]
        values = (
            profile.display_name,
            review.access_application_state,
            review.documentary_status,
            review.compatibility_status,
            missing_documents,
            missing_fields,
            review.external_activation_state,
        )
        return "<tr>" + "".join(f"<td><code>{html.escape(value)}</code></td>" for value in values) + "</tr>"

    def dispatch(self, method: str, raw_path: str) -> ConsoleResponse:
        normalized_method = method.upper().strip()
        if urlsplit(raw_path).path != ROUTE:
            return self.base_application.dispatch(normalized_method, raw_path)
        if normalized_method not in {"GET", "HEAD"}:
            return ConsoleResponse(
                status=405,
                content_type="text/plain; charset=utf-8",
                body=b"Method Not Allowed",
                headers=(("Allow", "GET, HEAD"), ("Cache-Control", "no-store")),
            )
        try:
            locale = self._locale(raw_path)
        except ValueError as exc:
            return ConsoleResponse(
                status=400,
                content_type="text/plain; charset=utf-8",
                body=b"" if normalized_method == "HEAD" else str(exc).encode("ascii"),
                headers=(("Cache-Control", "no-store"),),
            )
        body = b"" if normalized_method == "HEAD" else self._document(locale).encode("ascii")
        return ConsoleResponse(
            status=200,
            content_type="text/html; charset=utf-8",
            body=body,
            headers=(("Cache-Control", "no-store"), ("Content-Language", locale)),
        )
