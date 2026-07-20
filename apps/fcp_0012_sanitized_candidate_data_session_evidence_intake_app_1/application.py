from __future__ import annotations

import html
from dataclasses import dataclass
from urllib.parse import parse_qsl, urlsplit

from apps.browser_product_console_runtime_app_1 import ConsoleResponse
from apps.fcp_0011_candidate_data_source_onboarding_evidence_review_app_1 import (
    CandidateDataSourceOnboardingApplication,
    CandidateSourceProfile,
)

from .contracts import CandidateSessionEvidence, RegisteredSessionEvidenceArtifact
from .review import review_candidate_session_evidence


ROUTE = "/data-source-session-evidence"


def _zh(value: str) -> str:
    return "".join(f"&#{ord(char)};" if ord(char) > 127 else char for char in value)


ZH = {
    "title": _zh("\u5019\u9009\u6570\u636e\u6e90\u4f1a\u8bdd\u8bc1\u636e\u5ba1\u67e5"),
    "candidate": _zh("\u5019\u9009\u6570\u636e\u6e90"),
    "license": _zh("\u8bb8\u53ef\u8bc1\u7c7b\u578b"),
    "remaining": _zh("\u5269\u4f59\u5929\u6570"),
    "quota": _zh("\u6d41\u91cf\u7528\u91cf"),
    "probe": _zh("\u53ea\u8bfb\u63a2\u6d4b"),
    "documents": _zh("\u8d44\u6599\u5b8c\u6574\u5ea6"),
    "fields": _zh("\u5b57\u6bb5\u517c\u5bb9\u5ea6"),
    "activation": _zh("\u5916\u90e8\u6fc0\u6d3b"),
    "notice": _zh(
        "\u672c\u9875\u53ea\u5c55\u793a\u5df2\u767b\u8bb0\u3001\u5df2\u8131\u654f\u7684\u672c\u5730\u4f1a\u8bdd\u8bc1\u636e\u3002"
        "\u5b83\u4e0d\u4fdd\u5b58\u5bc6\u94a5\u6216\u884c\u60c5\u503c\uff0c\u4e0d\u4f1a\u9009\u62e9\u4f9b\u5e94\u5546\u6216\u6279\u51c6\u5916\u90e8\u6fc0\u6d3b\u3002"
    ),
    "back": _zh("\u8fd4\u56de\u5019\u9009\u6570\u636e\u6e90\u5ba1\u67e5"),
    "language": _zh("\u663e\u793a\u8bed\u8a00"),
}


@dataclass(frozen=True)
class SanitizedSessionEvidenceApplication:
    base_application: CandidateDataSourceOnboardingApplication
    profile: CandidateSourceProfile
    registration: RegisteredSessionEvidenceArtifact
    evidence: CandidateSessionEvidence

    def __post_init__(self) -> None:
        if not isinstance(self.base_application, CandidateDataSourceOnboardingApplication):
            raise TypeError("base_application must be the FCP-0011 console")
        review_candidate_session_evidence(self.profile, self.registration, self.evidence)

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
        packet = review_candidate_session_evidence(
            self.profile,
            self.registration,
            self.evidence,
        )
        labels = ZH if locale == "zh-CN" else {
            "title": "Candidate Session Evidence Review",
            "candidate": "Candidate",
            "license": "License class",
            "remaining": "Remaining days",
            "quota": "Quota usage",
            "probe": "Read-only probe",
            "documents": "Documentary status",
            "fields": "Field compatibility",
            "activation": "External activation",
            "notice": (
                "This page presents exact registered sanitized local session evidence only. "
                "It stores no secret or market value and cannot select or activate a provider."
            ),
            "back": "Back to candidate review",
            "language": "Presentation language",
        }
        other = "en" if locale == "zh-CN" else "zh-CN"
        quota = f"{packet.quota_used_bytes}/{packet.quota_limit_bytes} bytes"
        probe = f"{packet.probe_kind}:{packet.probe_status}:{packet.probe_row_count}"
        values = (
            self.profile.display_name,
            packet.license_class,
            str(packet.remaining_days),
            quota,
            probe,
            packet.documentary_status,
            packet.compatibility_status,
            packet.external_activation_state,
        )
        row = "<tr>" + "".join(
            f"<td><code>{html.escape(value)}</code></td>" for value in values
        ) + "</tr>"
        headings = (
            "candidate",
            "license",
            "remaining",
            "quota",
            "probe",
            "documents",
            "fields",
            "activation",
        )
        return (
            "<!doctype html><html><head><meta charset=\"utf-8\">"
            f"<title>{labels['title']}</title>"
            "<style>body{font-family:Arial,sans-serif;margin:0;background:#f3f0e8;color:#10222b}"
            "header{background:#0d3038;color:#fff;padding:20px}main{padding:24px}"
            "table{border-collapse:collapse;width:100%;background:#fff}th,td{border:1px solid #ddd;padding:10px}"
            "th{background:#e8eef0;text-align:left}.notice{border-left:4px solid #c56d35;background:#fff7eb;padding:12px;margin:16px 0}"
            "code{white-space:normal;word-break:break-word}</style></head><body>"
            f"<header><h1>{labels['title']}</h1><small>{labels['language']}: "
            f"<strong>{html.escape(locale)}</strong> / <a style=\"color:#fff\" href=\"{ROUTE}?lang={other}\">{other}</a></small></header>"
            f"<main><p><a href=\"/data-source-onboarding?lang={locale}\">{labels['back']}</a></p>"
            f"<div class=\"notice\">{labels['notice']}</div><table><thead><tr>"
            + "".join(f"<th>{labels[key]}</th>" for key in headings)
            + f"</tr></thead><tbody>{row}</tbody></table></main></body></html>"
        )

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
