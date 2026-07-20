from __future__ import annotations

import html
from dataclasses import dataclass
from urllib.parse import parse_qsl, urlsplit

from apps.browser_product_console_runtime_app_1 import ConsoleResponse
from apps.fcp_0013_candidate_data_evidence_bundle_reconciliation_app_1 import (
    CandidateEvidenceBundleApplication,
)

from .contracts import CandidateEvidenceGapRemediationPlan


ROUTE = "/data-source-evidence-remediation"


def _zh(value: str) -> str:
    return "".join(f"&#{ord(char)};" if ord(char) > 127 else char for char in value)


ZH = {
    "title": _zh("\u6570\u636e\u6e90\u8bc1\u636e\u7f3a\u53e3\u6574\u6539\u8ba1\u5212"),
    "priority": _zh("\u4f18\u5148\u7ea7"),
    "category": _zh("\u7f3a\u53e3\u7c7b\u522b"),
    "blocker": _zh("\u963b\u65ad\u7c7b\u578b"),
    "criteria": _zh("\u9a8c\u6536\u6761\u4ef6"),
    "fields": _zh("\u7f3a\u5931\u5b57\u6bb5"),
    "open": _zh("\u5f85\u6574\u6539\u9879"),
    "state": _zh("\u8ba1\u5212\u72b6\u6001"),
    "activation": _zh("\u5916\u90e8\u6fc0\u6d3b"),
    "language": _zh("\u663e\u793a\u8bed\u8a00"),
    "back": _zh("\u8fd4\u56de\u8bc1\u636e\u5305\u5bf9\u8d26"),
    "notice": _zh(
        "\u672c\u9875\u53ea\u5c55\u793a\u5df2\u767b\u8bb0\u8bc1\u636e\u4e2d\u7684\u672a\u89e3\u51b3\u7f3a\u53e3\u3002"
        "\u5b83\u4e0d\u63a5\u6536\u5bc6\u7801\u3001Token\u3001\u8d26\u6237\u6216\u8eab\u4efd\u4fe1\u606f\uff0c"
        "\u4e0d\u4f1a\u8054\u7cfb\u3001\u9009\u62e9\u6216\u6fc0\u6d3b\u4efb\u4f55\u6570\u636e\u4f9b\u5e94\u5546\u3002"
    ),
}
EN = {
    "title": "Candidate Data Evidence Gap Remediation Plan",
    "priority": "Priority",
    "category": "Gap category",
    "blocker": "Blocker kind",
    "criteria": "Acceptance criteria",
    "fields": "Missing fields",
    "open": "Open requirements",
    "state": "Plan state",
    "activation": "External activation",
    "language": "Presentation language",
    "back": "Back to evidence bundle reconciliation",
    "notice": (
        "This page presents unresolved gaps from registered evidence only. "
        "It accepts no credentials or account identity and cannot contact, select, purchase, or activate a provider."
    ),
}


@dataclass(frozen=True)
class EvidenceGapRemediationApplication:
    base_application: CandidateEvidenceBundleApplication
    plan: CandidateEvidenceGapRemediationPlan

    def __post_init__(self) -> None:
        if not isinstance(self.base_application, CandidateEvidenceBundleApplication):
            raise TypeError("base_application must be the FCP-0013 console")
        if not isinstance(self.plan, CandidateEvidenceGapRemediationPlan):
            raise TypeError("plan must be CandidateEvidenceGapRemediationPlan")

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
        labels = ZH if locale == "zh-CN" else EN
        other = "en" if locale == "zh-CN" else "zh-CN"
        rows = "".join(
            "<tr>"
            f"<td><strong>{item.priority}</strong></td>"
            f"<td><code>{html.escape(item.category)}</code></td>"
            f"<td><code>{html.escape(item.blocker_kind)}</code></td>"
            f"<td><code>{html.escape(', '.join(item.acceptance_criteria))}</code></td>"
            f"<td><code>{html.escape(', '.join(item.required_fields) or '-')}</code></td>"
            "</tr>"
            for item in self.plan.requirements
        )
        cards = (
            (labels["open"], str(len(self.plan.requirements))),
            (labels["state"], self.plan.plan_state),
            (labels["activation"], self.plan.external_activation_state),
        )
        card_html = "".join(
            f'<div class="card"><span>{label}</span><strong>{html.escape(value)}</strong></div>'
            for label, value in cards
        )
        return (
            '<!doctype html><html><head><meta charset="utf-8">'
            f"<title>{labels['title']}</title>"
            "<style>body{font-family:Arial,sans-serif;margin:0;background:#f3f0e8;color:#10222b}"
            "header{background:#0d3038;color:#fff;padding:20px}main{padding:24px}"
            ".grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}"
            ".card{background:#fff;border:1px solid #ddd;padding:14px}"
            ".card span,.card strong{display:block;margin:4px 0}"
            "table{border-collapse:collapse;width:100%;background:#fff;margin-top:18px}"
            "th,td{border:1px solid #ddd;padding:9px;vertical-align:top}"
            "th{background:#e8eef0;text-align:left}.notice{border-left:4px solid #c56d35;"
            "background:#fff7eb;padding:12px;margin:16px 0}code{white-space:normal;word-break:break-word}"
            "@media(max-width:900px){.grid{grid-template-columns:1fr}}</style></head><body>"
            f"<header><h1>{labels['title']}</h1><small>{labels['language']}: "
            f'<strong>{locale}</strong> / <a style="color:#fff" href="{ROUTE}?lang={other}">{other}</a>'
            "</small></header>"
            f'<main><p><a href="/data-source-evidence-bundle?lang={locale}">{labels["back"]}</a></p>'
            f'<div class="notice">{labels["notice"]}</div><div class="grid">{card_html}</div>'
            f"<table><thead><tr><th>{labels['priority']}</th><th>{labels['category']}</th>"
            f"<th>{labels['blocker']}</th><th>{labels['criteria']}</th>"
            f"<th>{labels['fields']}</th></tr></thead><tbody>{rows}</tbody></table>"
            "</main></body></html>"
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
