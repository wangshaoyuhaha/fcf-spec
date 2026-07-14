from __future__ import annotations

import html
import json
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Mapping, Tuple
from urllib.parse import urlsplit

from .boundary import ConsoleRuntimeConfig
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
_NAVIGATION = tuple(
    (route.path, route.title)
    for route in RESEARCH_WORKSPACE_ROUTE_REGISTRY.routes
    if route.path in _D4_IMPLEMENTED_PATHS
)


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def _layout(title: str, active_path: str, body: str) -> bytes:
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
code{{white-space:pre-wrap;overflow-wrap:anywhere}}
</style>
</head>
<body>
<header>
<strong>FCF Browser Product Console</strong>
<small>Paper-only / Local loopback / Operator review required</small>
</header>
<nav>{links}</nav>
<main>{body}</main>
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

    @property
    def read_model(self) -> ConsoleReadModel:
        return self._read_model

    def dispatch(self, method: str, raw_path: str) -> ConsoleResponse:
        normalized_method = method.upper().strip()
        path = urlsplit(raw_path).path or "/"

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
            headers=(
                ("Cache-Control", "no-store"),
                ("X-Content-Type-Options", "nosniff"),
                (
                    "Content-Security-Policy",
                    "default-src 'self'; style-src 'unsafe-inline'",
                ),
            ),
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
        return _layout("FCF Overview", path, body)

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
        return _layout("FCF Data Workspace", path, body)


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
        return _layout("FCF Research Runs", path, body)

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
        return _layout("FCF AI Comparison", path, body)

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
        return _layout("FCF Stock Candidates", path, body)


    def _governance_page(self, path: str) -> bytes:
        model = build_governance_workspace_model(self._read_model)
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
{table}
<section class="notice">
Governance evidence is registered-artifact-only and read-only. Deterministic
Engine authority and mandatory Operator review remain unchanged. This page
cannot approve, promote, replace a baseline, activate learning, or execute.
</section>
"""
        return _layout("FCF Governance", path, body)

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
        return _layout("FCF Audit History", path, body)

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
                    payload,
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
        return _layout(f"FCF {title}", path, body)

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
) -> ThreadingHTTPServer:
    config.resolve_allowed_root()

    class ConsoleRequestHandler(BaseHTTPRequestHandler):
        def _handle(self) -> None:
            response = application.dispatch(self.command, self.path)
            self.send_response(response.status)
            self.send_header("Content-Type", response.content_type)
            self.send_header("Content-Length", str(len(response.body)))
            for name, value in response.headers:
                self.send_header(name, value)
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(response.body)

        do_GET = _handle
        do_HEAD = _handle
        do_POST = _handle
        do_PUT = _handle
        do_DELETE = _handle
        do_PATCH = _handle

        def log_message(self, format: str, *args: object) -> None:
            return

    server = ThreadingHTTPServer(
        (config.host, config.port),
        ConsoleRequestHandler,
    )
    if server.server_address[0] != "127.0.0.1":
        server.server_close()
        raise RuntimeError("console server did not bind to loopback")
    return server
