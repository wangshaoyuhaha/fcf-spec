from __future__ import annotations

import html
from dataclasses import dataclass
from urllib.parse import parse_qsl, urlsplit

from apps.browser_product_console_runtime_app_1 import ConsoleResponse
from apps.fcp_0012_sanitized_candidate_data_session_evidence_intake_app_1 import (
    SanitizedSessionEvidenceApplication,
)

from .contracts import CandidateEvidenceBundle
from .reconciliation import reconcile_candidate_evidence_bundle


ROUTE = "/data-source-evidence-bundle"


def _zh(value: str) -> str:
    return "".join(f"&#{ord(char)};" if ord(char) > 127 else char for char in value)


ZH = {
    "title": _zh("\u5019\u9009\u6570\u636e\u6e90\u8bc1\u636e\u5305\u5bf9\u8d26"),
    "source": _zh("\u6ce8\u518c\u8bc1\u636e"),
    "kind": _zh("\u8bc1\u636e\u7c7b\u578b"),
    "range": _zh("\u89c2\u6d4b\u65e5\u671f"),
    "capability": _zh("\u5df2\u89c2\u6d4b\u80fd\u529b"),
    "delta": _zh("\u5c31\u7eea\u5ea6\u53d8\u5316"),
    "missing": _zh("\u4ecd\u7f3a\u5931\u8bc1\u636e"),
    "conflict": _zh("\u51b2\u7a81\u6570"),
    "activation": _zh("\u5916\u90e8\u6fc0\u6d3b"),
    "language": _zh("\u663e\u793a\u8bed\u8a00"),
    "back": _zh("\u8fd4\u56de\u4f1a\u8bdd\u8bc1\u636e\u5ba1\u67e5"),
    "notice": _zh(
        "\u672c\u9875\u53ea\u5bf9\u8d26\u5df2\u767b\u8bb0\u7684\u672c\u5730\u8bc1\u636e\u5f15\u7528\u3002"
        "\u5b83\u4e0d\u8054\u7f51\uff0c\u4e0d\u4fdd\u5b58\u5bc6\u94a5\u6216\u4f9b\u5e94\u5546\u539f\u59cb\u6570\u636e\uff0c"
        "\u4e0d\u4f1a\u9009\u62e9\u4f9b\u5e94\u5546\u6216\u6279\u51c6\u5b9e\u65f6\u4f7f\u7528\u3002"
    ),
}


EN = {
    "title": "Candidate Data Evidence Bundle Reconciliation",
    "source": "Registered evidence",
    "kind": "Evidence kind",
    "range": "Observation range",
    "capability": "Observed capability",
    "delta": "Readiness delta",
    "missing": "Missing evidence",
    "conflict": "Conflict count",
    "activation": "External activation",
    "language": "Presentation language",
    "back": "Back to session evidence review",
    "notice": (
        "This page reconciles registered local evidence references only. "
        "It uses no network, secret, or raw provider bytes and cannot select or activate a provider."
    ),
}


@dataclass(frozen=True)
class CandidateEvidenceBundleApplication:
    base_application: SanitizedSessionEvidenceApplication
    bundle: CandidateEvidenceBundle

    def __post_init__(self) -> None:
        if not isinstance(self.base_application, SanitizedSessionEvidenceApplication):
            raise TypeError("base_application must be the FCP-0012 console")
        reconcile_candidate_evidence_bundle(self.bundle)

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
        packet = reconcile_candidate_evidence_bundle(self.bundle)
        labels = ZH if locale == "zh-CN" else EN
        other = "en" if locale == "zh-CN" else "zh-CN"
        rows = "".join(
            "<tr>"
            f"<td><code>{html.escape(reference.evidence_id)}</code></td>"
            f"<td><code>{html.escape(reference.evidence_kind)}</code></td>"
            f"<td><code>{html.escape(reference.observed_from)} / {html.escape(reference.observed_to)}</code></td>"
            f"<td><code>{html.escape(', '.join(reference.observed_capabilities))}</code></td>"
            "</tr>"
            for reference in self.bundle.references
        )
        summary = (
            (labels["delta"], packet.readiness_delta),
            (labels["missing"], str(len(packet.missing_evidence_categories))),
            (labels["conflict"], str(len(packet.conflict_codes))),
            (labels["activation"], packet.external_activation_state),
        )
        cards = "".join(
            f'<div class="card"><span>{label}</span><strong>{html.escape(value)}</strong></div>'
            for label, value in summary
        )
        return (
            '<!doctype html><html><head><meta charset="utf-8">'
            f"<title>{labels['title']}</title>"
            "<style>body{font-family:Arial,sans-serif;margin:0;background:#f3f0e8;color:#10222b}"
            "header{background:#0d3038;color:#fff;padding:20px}main{padding:24px}"
            ".grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}"
            ".card{background:#fff;border:1px solid #ddd;padding:14px}"
            ".card span,.card strong{display:block;margin:4px 0}"
            "table{border-collapse:collapse;width:100%;background:#fff;margin-top:18px}"
            "th,td{border:1px solid #ddd;padding:10px}th{background:#e8eef0;text-align:left}"
            ".notice{border-left:4px solid #c56d35;background:#fff7eb;padding:12px;margin:16px 0}"
            "code{white-space:normal;word-break:break-word}"
            "@media(max-width:900px){.grid{grid-template-columns:1fr 1fr}}</style></head><body>"
            f"<header><h1>{labels['title']}</h1><small>{labels['language']}: "
            f'<strong>{html.escape(locale)}</strong> / <a style="color:#fff" '
            f'href="{ROUTE}?lang={other}">{other}</a></small></header>'
            f'<main><p><a href="/data-source-session-evidence?lang={locale}">{labels["back"]}</a></p>'
            f'<div class="notice">{labels["notice"]}</div><div class="grid">{cards}</div>'
            f"<table><thead><tr><th>{labels['source']}</th><th>{labels['kind']}</th>"
            f"<th>{labels['range']}</th><th>{labels['capability']}</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></main></body></html>"
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
