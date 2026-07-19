from __future__ import annotations

import html
import json
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler
from typing import Mapping, Tuple
from urllib.parse import urlsplit

from .boundary import ConsoleRuntimeConfig
from .runtime_lifecycle import (
    HardenedLoopbackHTTPServer,
    create_hardened_loopback_server,
    host_header_is_valid,
)
from .runtime_diagnostics import RuntimeFaultCode
from .runtime_hardening import (
    BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_LIMITS,
)
from .runtime_http import assess_runtime_request
from .evidence_audit_explorer import (
    EVIDENCE_AUDIT_EXPLORER_ROUTE_REGISTRY,
)
from .evidence_audit_views import (
    build_evidence_audit_explorer_page,
)
from .read_model import ConsoleReadModel, StockCandidateCard
from .research_workspace import RESEARCH_WORKSPACE_ROUTE_REGISTRY
from .research_workspace_views import (
    build_ai_comparison_workspace_model,
    build_audit_history_workspace_model,
    build_data_workspace_model,
    build_governance_workspace_model,
    build_overview_workspace_model,
    build_research_runs_workspace_model,
)


@dataclass(frozen=True)
class ConsoleResponse:
    status: int
    content_type: str
    body: bytes
    headers: Tuple[Tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if self.status < 100 or self.status > 599:
            raise ValueError("invalid HTTP status")
        if not self.content_type.strip():
            raise ValueError("content_type is required")


_D4_IMPLEMENTED_PATHS = frozenset(
    {
        "/",
        "/data",
        "/stocks",
        "/runs",
        "/ai-comparison",
        "/risk",
        "/validation",
        "/review",
        "/reports",
        "/governance",
        "/audit",
    }
)
_NAVIGATION = (
    tuple(
        (route.path, route.title)
        for route in RESEARCH_WORKSPACE_ROUTE_REGISTRY.routes
        if route.path in _D4_IMPLEMENTED_PATHS
    )
    + EVIDENCE_AUDIT_EXPLORER_ROUTE_REGISTRY.navigation()
)
_EVIDENCE_AUDIT_PATHS = frozenset(
    route.path
    for route in EVIDENCE_AUDIT_EXPLORER_ROUTE_REGISTRY.routes
)
_SECURITY_HEADERS = (
    ("Cache-Control", "no-store"),
    ("X-Content-Type-Options", "nosniff"),
    (
        "Content-Security-Policy",
        "default-src 'self'; style-src 'unsafe-inline'",
    ),
)


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def _layout(
    title: str,
    active_path: str,
    body: str,
    *,
    data_classification: str = "REGISTERED_EVIDENCE",
) -> bytes:
    links = "".join(
        (
            f'<a class="{"active" if path == active_path else ""}" '
            f'href="{path}">{_escape(label)}</a>'
        )
        for path, label in _NAVIGATION
    )
    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_escape(title)}</title>
<style>
body{{font-family:Arial,sans-serif;margin:0;background:#f4f6f8;color:#17202a}}
header{{background:#111827;color:#fff;padding:18px 24px}}
header small{{display:block;color:#cbd5e1;margin-top:4px}}
nav{{background:#1f2937;padding:10px 24px;display:flex;gap:12px;flex-wrap:wrap}}
nav a{{color:#d1d5db;text-decoration:none;padding:8px 10px;border-radius:6px}}
nav a.active{{background:#374151;color:#fff}}
main{{padding:24px;max-width:1280px;margin:auto}}
.card{{background:#fff;border:1px solid #d8dee6;border-radius:10px;padding:18px;margin-bottom:16px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}}
.badge{{display:inline-block;background:#e8eef7;border-radius:999px;padding:4px 8px;margin:2px;font-size:12px}}
.risk{{background:#fff1f2}}
.state{{font-weight:bold}}
table{{border-collapse:collapse;width:100%}}
th,td{{border-bottom:1px solid #e5e7eb;text-align:left;padding:10px;vertical-align:top}}
th{{background:#f8fafc}}
.notice{{border-left:4px solid #b45309;background:#fffbeb;padding:12px}}
.classification{{border-left:4px solid #b91c1c;background:#fef2f2;padding:12px;margin-bottom:16px}}
code{{white-space:pre-wrap;overflow-wrap:anywhere}}
</style>
</head>
<body>
<header>
<strong>FCF Browser Product Console</strong>
<small>Paper-only / Local loopback / Operator review required</small>
</header>
<nav>{links}</nav>
<main>
<section class="classification">
Data classification: <strong>{_escape(data_classification)}</strong>.
Verify registered evidence and complete Operator review before any decision.
</section>
{body}
</main>
</body>
</html>
"""
    return document.encode("utf-8")


def _candidate_row(candidate: StockCandidateCard) -> str:
    breakdown = "<br>".join(
        f"{_escape(name)}: {_escape(score)}"
        for name, score in candidate.score_breakdown.items()
    )
    reasons = "".join(
        f'<span class="badge">{_escape(code)}</span>'
        for code in candidate.reason_codes
    ) or "-"
    risks = "".join(
        f'<span class="badge risk">{_escape(flag)}</span>'
        for flag in candidate.risk_flags
    ) or "-"
    return (
        "<tr>"
        f"<td>{candidate.rank}</td>"
        f"<td>{_escape(candidate.symbol)}</td>"
        f"<td>{_escape(candidate.name)}</td>"
        f"<td>{candidate.total_score:.2f}</td>"
        f"<td>{breakdown}</td>"
        f"<td>{reasons}</td>"
        f"<td>{risks}</td>"
        f"<td>{_escape(candidate.data_quality_state)}</td>"
        f"<td>{_escape(candidate.confidence_level)}</td>"
        "</tr>"
    )


class BrowserProductConsoleApplication:
    def __init__(self, read_model: ConsoleReadModel) -> None:
        self._read_model = read_model
        classifications = {
            str(payload.get("data_classification", "")).strip()
            for payloads in read_model.sections.values()
            for payload in payloads
            if str(payload.get("data_classification", "")).strip()
        }
        self._data_classification = (
            next(iter(classifications))
            if len(classifications) == 1
            else (
                "MIXED_REGISTERED_EVIDENCE"
                if classifications
                else "REGISTERED_EVIDENCE"
            )
        )

    @property
    def read_model(self) -> ConsoleReadModel:
        return self._read_model

    def _render_layout(self, title: str, path: str, body: str) -> bytes:
        return _layout(
            title,
            path,
            body,
            data_classification=self._data_classification,
        )

    def dispatch(self, method: str, raw_path: str) -> ConsoleResponse:
        normalized_method = method.upper().strip()
        split_result = urlsplit(raw_path)
        path = split_result.path or "/"

        if normalized_method not in {"GET", "HEAD"}:
            return self._text_response(405, "Method Not Allowed")

        if path == "/health":
            payload = json.dumps(
                {
                    "status": "ok",
                    "mode": "paper-only",
                    "host_scope": "loopback-only",
                    "operator_review_required": True,
                    "correlation_id": self._read_model.correlation_id,
                },
                sort_keys=True,
            ).encode("utf-8")
            return self._finalize(
                normalized_method,
                ConsoleResponse(
                    status=200,
                    content_type="application/json; charset=utf-8",
                    body=payload,
                ),
            )

        if path in _EVIDENCE_AUDIT_PATHS:
            try:
                page = build_evidence_audit_explorer_page(
                    self._read_model,
                    path,
                    split_result.query,
                )
                response = ConsoleResponse(
                    status=200,
                    content_type="text/html; charset=utf-8",
                    body=self._render_layout(
                        page.title,
                        path,
                        page.body_html,
                    ),
                    headers=_SECURITY_HEADERS,
                )
            except ValueError as exc:
                rejected_body = (
                    '<section class="card">'
                    "<h1>Evidence Audit query rejected</h1>"
                    '<p>State: <span class="state">'
                    "REJECTED_QUERY"
                    "</span></p>"
                    f"<p>{_escape(exc)}</p>"
                    "</section>"
                    '<section class="notice">'
                    "The query failed closed. No evidence was mutated, "
                    "approved, promoted, archived, or executed."
                    "</section>"
                )
                response = ConsoleResponse(
                    status=400,
                    content_type="text/html; charset=utf-8",
                    body=self._render_layout(
                        "FCF Evidence Audit Query Rejected",
                        path,
                        rejected_body,
                    ),
                    headers=_SECURITY_HEADERS,
                )
            return self._finalize(
                normalized_method,
                response,
            )

        page_builders = {
            "/": self._overview_page,
            "/data": self._data_page,
            "/stocks": self._stocks_page,
            "/runs": self._runs_page,
            "/ai-comparison": self._ai_comparison_page,
            "/risk": self._risk_page,
            "/validation": self._validation_page,
            "/review": self._review_page,
            "/reports": self._reports_page,
            "/governance": self._governance_page,
            "/audit": self._audit_page,
        }
        builder = page_builders.get(path)
        if builder is None:
            return self._text_response(404, "Not Found")

        response = ConsoleResponse(
            status=200,
            content_type="text/html; charset=utf-8",
            body=builder(path),
            headers=_SECURITY_HEADERS,
        )
        return self._finalize(normalized_method, response)

    @staticmethod
    def _finalize(method: str, response: ConsoleResponse) -> ConsoleResponse:
        if method == "HEAD":
            return ConsoleResponse(
                status=response.status,
                content_type=response.content_type,
                body=b"",
                headers=response.headers,
            )
        return response

    def _text_response(self, status: int, message: str) -> ConsoleResponse:
        return ConsoleResponse(
            status=status,
            content_type="text/plain; charset=utf-8",
            body=message.encode("utf-8"),
            headers=(("Cache-Control", "no-store"),),
        )

    def _overview_page(self, path: str) -> bytes:
        model = build_overview_workspace_model(self._read_model)
        type_counts = "".join(
            f"<li>{_escape(name)}: {count}</li>"
            for name, count in model.artifact_type_counts.items()
        )
        available = "".join(
            f"<li><code>{_escape(route)}</code></li>"
            for route in model.available_workspace_paths
        )
        planned = "".join(
            f"<li><code>{_escape(route)}</code></li>"
            for route in model.planned_workspace_paths
        )
        body = f"""
<section class="grid">
<section class="card">
<h1>Overview</h1>
<p>Correlation ID: <code>{_escape(model.correlation_id)}</code></p>
<p>Registered artifacts: {model.registered_artifact_count}</p>
<p>Stock candidates: {model.stock_candidate_count}</p>
</section>
<section class="card">
<h2>Workspace state</h2>
<p>Available: {len(model.available_workspace_paths)}</p>
<p>Planned: {len(model.planned_workspace_paths)}</p>
</section>
</section>
<section class="card">
<h2>Registered artifact types</h2>
<ul>{type_counts or "<li>No registered artifact records</li>"}</ul>
</section>
<section class="grid">
<section class="card">
<h2>Available workspaces</h2>
<ul>{available}</ul>
</section>
<section class="card">
<h2>Planned workspaces</h2>
<ul>{planned or "<li>None</li>"}</ul>
</section>
</section>
<section class="notice">
This console does not provide trading, order, broker, exchange, account,
balance, position, wallet, promotion, or automatic approval authority.
</section>
"""
        return self._render_layout("FCF Overview", path, body)

    def _data_page(self, path: str) -> bytes:
        model = build_data_workspace_model(self._read_model)
        rows = []
        for item in model.items:
            serialized = json.dumps(
                dict(item.payload),
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            )
            rows.append(
                (
                    "<tr>"
                    f"<td>{_escape(item.artifact_id)}</td>"
                    f"<td>{_escape(item.artifact_type)}</td>"
                    f"<td>{_escape(item.relative_path)}</td>"
                    f"<td><code>{_escape(item.content_sha256)}</code></td>"
                    f"<td><code>{_escape(serialized)}</code></td>"
                    "</tr>"
                )
            )
        table = (
            """
<section class="card">
<table>
<thead><tr>
<th>Artifact ID</th><th>Type</th><th>Registered path</th>
<th>SHA-256</th><th>Payload</th>
</tr></thead>
<tbody>{rows}</tbody>
</table>
</section>
""".format(rows="".join(rows))
            if rows
            else (
                '<section class="card">'
                "No registered data_snapshot or data_quality artifacts."
                "</section>"
            )
        )
        counts = "".join(
            f'<span class="badge">{_escape(name)}: {count}</span>'
            for name, count in model.artifact_type_counts.items()
        ) or '<span class="badge">No registered data artifacts</span>'
        body = f"""
<section class="card">
<h1>Data Workspace</h1>
<p>Correlation ID: <code>{_escape(model.correlation_id)}</code></p>
<p>State: <span class="state">{_escape(model.state)}</span></p>
<p>{counts}</p>
</section>
{table}
<section class="notice">
Registered-artifact-only and read-only. External data fetching, mutation,
automatic promotion, and execution are prohibited.
</section>
"""
        return self._render_layout("FCF Data Workspace", path, body)


    def _runs_page(self, path: str) -> bytes:
        model = build_research_runs_workspace_model(self._read_model)
        rows = []
        for item in model.items:
            serialized = json.dumps(
                dict(item.payload),
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            )
            rows.append(
                (
                    "<tr>"
                    f"<td>{_escape(item.artifact_id)}</td>"
                    f"<td>{_escape(item.artifact_type)}</td>"
                    f"<td>{_escape(item.run_id)}</td>"
                    f"<td>{_escape(item.workflow_state)}</td>"
                    f"<td>{_escape(item.relative_path)}</td>"
                    f"<td><code>{_escape(item.content_sha256)}</code></td>"
                    f"<td><code>{_escape(serialized)}</code></td>"
                    "</tr>"
                )
            )
        table = (
            """
<section class="card">
<table>
<thead><tr>
<th>Artifact ID</th><th>Type</th><th>Run ID</th>
<th>Workflow state</th><th>Registered path</th>
<th>SHA-256</th><th>Payload</th>
</tr></thead>
<tbody>{rows}</tbody>
</table>
</section>
""".format(rows="".join(rows))
            if rows
            else (
                '<section class="card">'
                "No registered research_run or workflow_status artifacts."
                "</section>"
            )
        )
        counts = "".join(
            f'<span class="badge">{_escape(name)}: {count}</span>'
            for name, count in model.artifact_type_counts.items()
        ) or '<span class="badge">No registered run artifacts</span>'
        body = f"""
<section class="card">
<h1>Research Runs</h1>
<p>Correlation ID: <code>{_escape(model.correlation_id)}</code></p>
<p>State: <span class="state">{_escape(model.state)}</span></p>
<p>{counts}</p>
</section>
{table}
<section class="notice">
Research run evidence is registered-artifact-only and read-only. This page
cannot dispatch workflows, mutate run state, promote artifacts, or execute
financial actions.
</section>
"""
        return self._render_layout("FCF Research Runs", path, body)

    def _ai_comparison_page(self, path: str) -> bytes:
        model = build_ai_comparison_workspace_model(self._read_model)
        rows = []
        for item in model.items:
            serialized = json.dumps(
                dict(item.payload),
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            )
            rows.append(
                (
                    "<tr>"
                    f"<td>{_escape(item.artifact_id)}</td>"
                    f"<td>{_escape(item.artifact_type)}</td>"
                    f"<td>{_escape(item.model_label)}</td>"
                    f"<td>{_escape(item.prompt_version)}</td>"
                    f"<td>{_escape(item.evaluation_state)}</td>"
                    f"<td>{_escape(item.relative_path)}</td>"
                    f"<td><code>{_escape(serialized)}</code></td>"
                    "</tr>"
                )
            )
        table = (
            """
<section class="card">
<table>
<thead><tr>
<th>Artifact ID</th><th>Type</th><th>Model</th>
<th>Prompt version</th><th>Evaluation state</th>
<th>Registered path</th><th>Payload</th>
</tr></thead>
<tbody>{rows}</tbody>
</table>
</section>
""".format(rows="".join(rows))
            if rows
            else (
                '<section class="card">'
                "No registered ai_explanation or ai_evaluation artifacts."
                "</section>"
            )
        )
        counts = "".join(
            f'<span class="badge">{_escape(name)}: {count}</span>'
            for name, count in model.artifact_type_counts.items()
        ) or '<span class="badge">No registered AI artifacts</span>'
        body = f"""
<section class="card">
<h1>AI Comparison</h1>
<p>Correlation ID: <code>{_escape(model.correlation_id)}</code></p>
<p>State: <span class="state">{_escape(model.state)}</span></p>
<p>{counts}</p>
</section>
{table}
<section class="notice">
AI output is advisory-only. Deterministic Engine authority and mandatory
Operator review remain unchanged. No automatic approval, promotion,
baseline replacement, learning activation, archive, or execution is allowed.
</section>
"""
        return self._render_layout("FCF AI Comparison", path, body)

    def _stocks_page(self, path: str) -> bytes:
        rows = "".join(
            _candidate_row(candidate)
            for candidate in self._read_model.candidates
        )
        if not rows:
            rows = '<tr><td colspan="9">No registered candidates</td></tr>'
        body = f"""
<section class="card">
<h1>Stock Candidates</h1>
<table>
<thead><tr>
<th>Rank</th><th>Symbol</th><th>Name</th><th>Total score</th>
<th>Score breakdown</th><th>Reason codes</th><th>Risk flags</th>
<th>Data quality</th><th>Confidence</th>
</tr></thead>
<tbody>{rows}</tbody>
</table>
</section>
<section class="notice">
Candidate information is research evidence only. Operator review is required.
</section>
"""
        return self._render_layout("FCF Stock Candidates", path, body)


    def _governance_page(self, path: str) -> bytes:
        model = build_governance_workspace_model(self._read_model)
        attention = model.attention_summary
        if attention is None:
            raise ValueError("Governance attention summary is required")
        confidence_badges = "".join(
            f'<span class="badge">{_escape(name)}: {count}</span>'
            for name, count in attention.confidence_counts.items()
        ) or '<span class="badge">No projection confidence</span>'
        attention_card = f"""
<section class="card governance-attention-summary">
<h2>Operator Attention Summary</h2>
<p>Attention state: <span class="state">{_escape(attention.status)}</span></p>
<div class="grid">
<p><strong>Projections</strong><br>{attention.projection_count}</p>
<p><strong>Operator review required</strong><br>{attention.operator_review_required_count}</p>
<p><strong>Blocked</strong><br>{attention.blocked_count}</p>
<p><strong>Incomplete</strong><br>{attention.incomplete_count}</p>
<p><strong>Observed fields</strong><br>{attention.observed_field_count}</p>
<p><strong>Inferred fields</strong><br>{attention.inferred_field_count}</p>
</div>
<p><strong>Projection confidence</strong><br>{confidence_badges}</p>
<p>This summary is read-only evidence presentation. It cannot approve,
promote, activate a factor, or create an action.</p>
</section>
"""
        review_reason_summary = model.review_reason_summary
        if review_reason_summary is None:
            raise ValueError("Governance review reason summary is required")
        reason_rows = "".join(
            "<tr>"
            f"<td>{_escape(item.reason_code)}</td>"
            f"<td>{item.occurrence_count}</td>"
            f"<td>{item.blocked_count}</td>"
            f"<td>{item.incomplete_count}</td>"
            f"<td>{item.review_required_count}</td>"
            "</tr>"
            for item in review_reason_summary.items
        )
        reason_table = (
            "<table><thead><tr><th>Reason code</th><th>Occurrences</th>"
            "<th>Blocked</th><th>Incomplete</th><th>Review required</th>"
            f"</tr></thead><tbody>{reason_rows}</tbody></table>"
            if reason_rows
            else "<p>No registered governance review reasons.</p>"
        )
        review_reason_summary_card = f"""
<section class="card governance-review-reason-summary">
<h2>Governance Review Reason Summary</h2>
<p>Reason state: <span class="state">{_escape(review_reason_summary.status)}</span></p>
<div class="grid">
<p><strong>Queue items</strong><br>{review_reason_summary.queue_item_count}</p>
<p><strong>Unique reasons</strong><br>{review_reason_summary.unique_reason_count}</p>
<p><strong>Reason occurrences</strong><br>{review_reason_summary.reason_occurrence_count}</p>
</div>
<p>Reason counts are derived deterministically from the read-only review queue.</p>
{reason_table}
</section>
"""
        review_coverage_summary = model.review_coverage_summary
        if review_coverage_summary is None:
            raise ValueError("Governance review coverage summary is required")
        coverage_rows = "".join(
            "<tr>"
            f"<td>{_escape(item.attention_class)}</td>"
            f"<td><code>{_escape(item.projection_id)}</code></td>"
            f"<td>{'REGISTERED' if item.evidence_registered else 'MISSING'}</td>"
            f"<td>{item.observed_field_count}</td>"
            f"<td>{item.inferred_field_count}</td>"
            f"<td>{item.source_snapshot_count}</td>"
            "</tr>"
            for item in review_coverage_summary.items
        )
        coverage_table = (
            "<table><thead><tr><th>Attention class</th><th>Projection</th>"
            "<th>Evidence coverage</th><th>Observed fields</th>"
            "<th>Inferred fields</th><th>Registered sources</th>"
            f"</tr></thead><tbody>{coverage_rows}</tbody></table>"
            if coverage_rows
            else "<p>No registered governance review items.</p>"
        )
        review_coverage_summary_card = f"""
<section class="card governance-review-coverage-summary">
<h2>Governance Review Coverage Summary</h2>
<p>Coverage state: <span class="state">{_escape(review_coverage_summary.status)}</span></p>
<div class="grid">
<p><strong>Queue items</strong><br>{review_coverage_summary.queue_item_count}</p>
<p><strong>Covered items</strong><br>{review_coverage_summary.covered_item_count}</p>
<p><strong>Missing evidence</strong><br>{review_coverage_summary.missing_evidence_count}</p>
<p><strong>Observed fields</strong><br>{review_coverage_summary.observed_field_count}</p>
<p><strong>Inferred fields</strong><br>{review_coverage_summary.inferred_field_count}</p>
<p><strong>Registered sources</strong><br>{review_coverage_summary.source_snapshot_count}</p>
</div>
<p>Coverage is derived deterministically from the read-only review queue and
registered evidence trace. Missing evidence remains visible for Operator review.</p>
{coverage_table}
</section>
"""
        review_market_summary = model.review_market_summary
        if review_market_summary is None:
            raise ValueError("Governance review market summary is required")
        market_rows = "".join(
            "<tr>"
            f"<td>{_escape(item.market)}</td><td>{item.queue_item_count}</td>"
            f"<td>{item.blocked_count}</td><td>{item.incomplete_count}</td>"
            f"<td>{item.review_required_count}</td><td>{item.covered_item_count}</td>"
            f"<td>{item.missing_evidence_count}</td></tr>"
            for item in review_market_summary.items
        )
        market_table = (
            "<table><thead><tr><th>Market</th><th>Queue items</th>"
            "<th>Blocked</th><th>Incomplete</th><th>Review required</th>"
            "<th>Covered items</th><th>Missing evidence</th>"
            f"</tr></thead><tbody>{market_rows}</tbody></table>"
            if market_rows
            else "<p>No registered governance review markets.</p>"
        )
        review_market_summary_card = f"""
<section class="card governance-review-market-summary">
<h2>Governance Review Market Summary</h2>
<p>Market state: <span class="state">{_escape(review_market_summary.status)}</span></p>
<div class="grid">
<p><strong>Markets</strong><br>{review_market_summary.market_count}</p>
<p><strong>Queue items</strong><br>{review_market_summary.queue_item_count}</p>
<p><strong>Covered items</strong><br>{review_market_summary.covered_item_count}</p>
<p><strong>Missing evidence</strong><br>{review_market_summary.missing_evidence_count}</p>
</div>
<p>Market counts are derived deterministically from registered review and
coverage evidence. They do not rank markets or create an action.</p>
{market_table}
</section>
"""
        review_queue = model.review_queue
        if review_queue is None:
            raise ValueError("Governance review queue is required")
        review_evidence_trace = model.review_evidence_trace
        if review_evidence_trace is None:
            raise ValueError("Governance review evidence trace is required")
        evidence_trace_by_key = {
            (item.artifact_id, item.projection_id): item
            for item in review_evidence_trace.items
        }
        queue_rows = []
        for item in review_queue.items:
            evidence_trace = evidence_trace_by_key[(item.artifact_id, item.projection_id)]
            reasons = "".join(
                f'<span class="badge">{_escape(reason)}</span>'
                for reason in item.reason_codes
            )
            queue_rows.append(
                "<tr>"
                f"<td>{_escape(item.attention_class)}</td>"
                f"<td>{_escape(item.candidate_id)}</td>"
                f"<td>{_escape(item.factor_id)}</td>"
                f"<td>{_escape(item.market)}</td>"
                f"<td>{_escape(item.state)}</td>"
                f"<td>{_escape(item.confidence)}</td>"
                f"<td>{evidence_trace.observed_field_count}</td>"
                f"<td>{evidence_trace.inferred_field_count}</td>"
                f"<td>{evidence_trace.source_snapshot_count}</td>"
                f"<td>{'<br>'.join(f'<code>{_escape(value)}</code>' for value in evidence_trace.source_snapshot_hashes)}</td>"
                f"<td>{reasons}</td>"
                f"<td><code>{_escape(item.projection_hash)}</code></td>"
                "</tr>"
            )
        queue_table = (
            """
<table>
<thead><tr><th>Attention class</th><th>Candidate</th><th>Factor</th>
<th>Market</th><th>State</th><th>Confidence</th><th>Observed fields</th>
<th>Inferred fields</th><th>Registered sources</th><th>Source snapshot hashes</th><th>Reason codes</th>
<th>Projection hash</th></tr></thead>
<tbody>{rows}</tbody>
</table>
""".format(rows="".join(queue_rows))
            if queue_rows
            else "<p>No registered governance review items.</p>"
        )
        review_queue_card = f"""
<section class="card governance-review-queue">
<h2>Operator Governance Review Queue</h2>
<p>Queue state: <span class="state">{_escape(review_queue.status)}</span></p>
<p>Items are ordered deterministically as blocked, incomplete, then review
required. Registered evidence traces preserve observed-versus-inferred counts
and source snapshot hashes. This queue is read-only and cannot approve or
activate a factor.</p>
{queue_table}
</section>
"""
        projection_sections = []
        for projection in model.projection_presentations:
            field_rows = []
            for field in projection.fields:
                sources = "<br>".join(
                    f"<code>{_escape(source)}</code>"
                    for source in field.source_snapshot_hashes
                )
                field_rows.append(
                    "<tr>"
                    f"<td>{_escape(field.field_id)}</td>"
                    f"<td>{_escape(field.value)}</td>"
                    f'<td><span class="badge">{_escape(field.origin)}</span></td>'
                    f"<td>{_escape(field.confidence)}</td>"
                    f"<td>{sources}</td>"
                    "</tr>"
                )
            reasons = "".join(
                f'<span class="badge">{_escape(reason)}</span>'
                for reason in projection.reason_codes
            )
            projection_sections.append(
                f"""
<section class="card governance-projection">
<h2>Factor Governance Field Detail</h2>
<div class="grid">
<p><strong>Candidate</strong><br>{_escape(projection.candidate_id)}</p>
<p><strong>Factor</strong><br>{_escape(projection.factor_id)}</p>
<p><strong>Market</strong><br>{_escape(projection.market)}</p>
<p><strong>State</strong><br>{_escape(projection.state)}</p>
<p><strong>Confidence</strong><br>{_escape(projection.confidence)}</p>
<p><strong>Evaluated at</strong><br>{_escape(projection.evaluated_at_utc)}</p>
</div>
<p><strong>Reason codes</strong><br>{reasons}</p>
<table>
<thead><tr><th>Field</th><th>Value</th><th>Origin</th>
<th>Confidence</th><th>Registered source snapshots</th></tr></thead>
<tbody>{''.join(field_rows)}</tbody>
</table>
<p>Projection hash: <code>{_escape(projection.projection_hash)}</code></p>
</section>
"""
            )
        rows = []
        for item in model.items:
            serialized = json.dumps(
                dict(item.payload),
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            )
            rows.append(
                (
                    "<tr>"
                    f"<td>{_escape(item.artifact_id)}</td>"
                    f"<td>{_escape(item.artifact_type)}</td>"
                    f"<td>{_escape(item.subject)}</td>"
                    f"<td>{_escape(item.version)}</td>"
                    f"<td>{_escape(item.decision)}</td>"
                    f"<td>{_escape(item.relative_path)}</td>"
                    f"<td><code>{_escape(item.content_sha256)}</code></td>"
                    f"<td><code>{_escape(serialized)}</code></td>"
                    "</tr>"
                )
            )
        table = (
            """
<section class="card">
<table>
<thead><tr>
<th>Artifact ID</th><th>Type</th><th>Subject</th>
<th>Version</th><th>Decision</th><th>Registered path</th>
<th>SHA-256</th><th>Payload</th>
</tr></thead>
<tbody>{rows}</tbody>
</table>
</section>
""".format(rows="".join(rows))
            if rows
            else (
                '<section class="card">'
                "No registered model_governance or policy_snapshot artifacts."
                "</section>"
            )
        )
        counts = "".join(
            f'<span class="badge">{_escape(name)}: {count}</span>'
            for name, count in model.artifact_type_counts.items()
        ) or '<span class="badge">No registered governance artifacts</span>'
        body = f"""
<section class="card">
<h1>Governance</h1>
<p>Correlation ID: <code>{_escape(model.correlation_id)}</code></p>
<p>State: <span class="state">{_escape(model.state)}</span></p>
<p>{counts}</p>
</section>
{attention_card}
{review_reason_summary_card}
{review_coverage_summary_card}
{review_market_summary_card}
{review_queue_card}
{''.join(projection_sections)}
{table}
<section class="notice">
Governance evidence is registered-artifact-only and read-only. Deterministic
Engine authority and mandatory Operator review remain unchanged. This page
cannot approve, promote, replace a baseline, activate learning, or execute.
</section>
"""
        return self._render_layout("FCF Governance", path, body)

    def _audit_page(self, path: str) -> bytes:
        model = build_audit_history_workspace_model(self._read_model)
        rows = []
        for item in model.items:
            serialized = json.dumps(
                dict(item.payload),
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            )
            rows.append(
                (
                    "<tr>"
                    f"<td>{_escape(item.artifact_id)}</td>"
                    f"<td>{_escape(item.artifact_type)}</td>"
                    f"<td>{_escape(item.event_id)}</td>"
                    f"<td>{_escape(item.event_time)}</td>"
                    f"<td>{_escape(item.action)}</td>"
                    f"<td>{_escape(item.actor)}</td>"
                    f"<td>{_escape(item.relative_path)}</td>"
                    f"<td><code>{_escape(serialized)}</code></td>"
                    "</tr>"
                )
            )
        table = (
            """
<section class="card">
<table>
<thead><tr>
<th>Artifact ID</th><th>Type</th><th>Event ID</th>
<th>Event time</th><th>Action</th><th>Actor</th>
<th>Registered path</th><th>Payload</th>
</tr></thead>
<tbody>{rows}</tbody>
</table>
</section>
""".format(rows="".join(rows))
            if rows
            else (
                '<section class="card">'
                "No registered audit_receipt or manifest artifacts."
                "</section>"
            )
        )
        counts = "".join(
            f'<span class="badge">{_escape(name)}: {count}</span>'
            for name, count in model.artifact_type_counts.items()
        ) or '<span class="badge">No registered audit artifacts</span>'
        body = f"""
<section class="card">
<h1>Audit History</h1>
<p>Correlation ID: <code>{_escape(model.correlation_id)}</code></p>
<p>State: <span class="state">{_escape(model.state)}</span></p>
<p>{counts}</p>
</section>
{table}
<section class="notice">
Audit History is an append-only evidence presentation. It cannot mutate,
delete, approve, promote, archive automatically, or execute financial actions.
</section>
"""
        return self._render_layout("FCF Audit History", path, body)

    def _section_page(
        self,
        path: str,
        title: str,
        artifact_types: Tuple[str, ...],
    ) -> bytes:
        cards = []
        for artifact_type in artifact_types:
            for payload in self._read_model.sections.get(
                artifact_type,
                (),
            ):
                serialized = json.dumps(
                    dict(payload),
                    indent=2,
                    sort_keys=True,
                    ensure_ascii=True,
                )
                cards.append(
                    (
                        '<section class="card">'
                        f"<h2>{_escape(artifact_type)}</h2>"
                        f"<code>{_escape(serialized)}</code>"
                        "</section>"
                    )
                )
        body = (
            f"<h1>{_escape(title)}</h1>"
            + (
                "".join(cards)
                if cards
                else '<section class="card">No registered evidence</section>'
            )
        )
        return self._render_layout(f"FCF {title}", path, body)

    def _risk_page(self, path: str) -> bytes:
        return self._section_page(
            path,
            "Evidence and Risk",
            ("ranked_watchlist", "ai_explanation"),
        )

    def _validation_page(self, path: str) -> bytes:
        return self._section_page(
            path,
            "Paper and Shadow Validation",
            ("paper_validation", "shadow_observation"),
        )

    def _review_page(self, path: str) -> bytes:
        return self._section_page(
            path,
            "Operator Review",
            ("operator_review",),
        )

    def _reports_page(self, path: str) -> bytes:
        return self._section_page(
            path,
            "Reports and Archive",
            ("report_archive",),
        )


def create_loopback_server(
    config: ConsoleRuntimeConfig,
    application: BrowserProductConsoleApplication,
) -> HardenedLoopbackHTTPServer:
    config.resolve_allowed_root()

    limits = (
        BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_LIMITS
    )

    class ConsoleRequestHandler(BaseHTTPRequestHandler):
        server_version = "FCFConsole"
        sys_version = ""
        protocol_version = "HTTP/1.1"

        def _send_runtime_rejection(
            self,
            status: int,
            message: str,
            extra_headers: Tuple[
                Tuple[str, str],
                ...,
            ] = (),
        ) -> None:
            body = message.encode("ascii")

            self.send_response(status)
            self.send_header(
                "Content-Type",
                "text/plain; charset=utf-8",
            )
            self.send_header(
                "Content-Length",
                str(len(body)),
            )

            emitted = set()

            for name, value in extra_headers:
                self.send_header(name, value)
                emitted.add(name.lower())

            for name, value in _SECURITY_HEADERS:
                if name.lower() not in emitted:
                    self.send_header(name, value)

            self.send_header(
                "Connection",
                "close",
            )
            self.end_headers()

            if self.command != "HEAD":
                self.wfile.write(body)

            self.close_connection = True

        def _host_is_valid(self) -> bool:
            values = tuple(
                self.headers.get_all(
                    "Host",
                    [],
                )
            )

            return host_header_is_valid(
                values,
                config.port,
            )

        def _raw_headers(
            self,
        ) -> Tuple[Tuple[str, str], ...]:
            return tuple(
                (
                    str(name),
                    str(value),
                )
                for name, value in self.headers.raw_items()
            )

        def _handle(self) -> None:
            assessment = assess_runtime_request(
                self.command,
                self.path,
                self._raw_headers(),
                limits,
            )

            if not assessment.accepted:
                self._send_runtime_rejection(
                    assessment.status,
                    assessment.message,
                    assessment.response_headers,
                )
                return

            if not self._host_is_valid():
                self._send_runtime_rejection(
                    400,
                    "Bad Request",
                )
                return

            try:
                response = application.dispatch(
                    self.command,
                    self.path,
                )
            except Exception:
                server = self.server

                if isinstance(
                    server,
                    HardenedLoopbackHTTPServer,
                ):
                    server.record_runtime_fault(
                        RuntimeFaultCode.APPLICATION_DISPATCH_FAILURE
                    )

                self._send_runtime_rejection(
                    500,
                    "Internal Server Error",
                )
                return

            self.send_response(response.status)
            self.send_header(
                "Content-Type",
                response.content_type,
            )
            self.send_header(
                "Content-Length",
                str(len(response.body)),
            )

            response_header_names = {
                name.lower()
                for name, _ in response.headers
            }

            for name, value in response.headers:
                self.send_header(name, value)

            for name, value in _SECURITY_HEADERS:
                if name.lower() not in response_header_names:
                    self.send_header(name, value)

            self.send_header(
                "Connection",
                "close",
            )
            self.end_headers()

            if self.command != "HEAD":
                self.wfile.write(response.body)

            self.close_connection = True

        do_GET = _handle
        do_HEAD = _handle
        do_POST = _handle
        do_PUT = _handle
        do_DELETE = _handle
        do_PATCH = _handle
        do_OPTIONS = _handle
        do_TRACE = _handle
        do_CONNECT = _handle

        def __getattr__(self, name: str):
            if name.startswith("do_"):
                return self._handle
            raise AttributeError(name)

        def log_message(
            self,
            format: str,
            *args: object,
        ) -> None:
            return

    server = create_hardened_loopback_server(
        config.host,
        config.port,
        ConsoleRequestHandler,
        limits=limits,
    )

    if server.server_address != (
        "127.0.0.1",
        config.port,
    ):
        server.server_close()
        raise RuntimeError(
            "console server did not bind to exact loopback"
        )

    return server
