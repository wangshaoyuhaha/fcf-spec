from __future__ import annotations

import html
import json
from dataclasses import asdict, dataclass
from typing import Any, Mapping, Tuple
from urllib.parse import urlsplit

from .boundary import FCF_WEB_CONSOLE_BOUNDARY
from .contracts import (
    FCF_WEB_CONSOLE_ROUTES,
    ConsoleActionReceipt,
    IntakeValidationReceipt,
    WebConsoleSnapshot,
)
from .controls import GovernedConsoleActionService
from .intake import GovernedIntakeService


_SECURITY_HEADERS = (
    ("Cache-Control", "no-store"),
    ("X-Content-Type-Options", "nosniff"),
    ("Referrer-Policy", "no-referrer"),
    (
        "Content-Security-Policy",
        "default-src 'self'; style-src 'unsafe-inline'; "
        "script-src 'unsafe-inline'; connect-src 'self'",
    ),
)


@dataclass(frozen=True)
class WebConsoleResponse:
    status: int
    content_type: str
    body: bytes
    headers: Tuple[Tuple[str, str], ...] = _SECURITY_HEADERS

    def __post_init__(self) -> None:
        if self.status < 100 or self.status > 599:
            raise ValueError("invalid HTTP status")


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def _json_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        dict(payload),
        ensure_ascii=True,
        sort_keys=True,
    ).encode("utf-8")


def _receipt_payload(receipt: object) -> Mapping[str, Any]:
    payload = asdict(receipt)
    if isinstance(receipt, IntakeValidationReceipt):
        payload["descriptors"] = [
            {
                **asdict(item),
                "kind": item.kind.value,
            }
            for item in receipt.descriptors
        ]
    if isinstance(receipt, ConsoleActionReceipt):
        payload["action"] = receipt.action.value
    return payload


class FCFWebConsoleApplication:
    def __init__(self, snapshot: WebConsoleSnapshot) -> None:
        self._snapshot = snapshot
        self._intake = GovernedIntakeService()
        self._actions = GovernedConsoleActionService()

    @property
    def snapshot(self) -> WebConsoleSnapshot:
        return self._snapshot

    def dispatch(
        self,
        method: str,
        raw_path: str,
        payload: Mapping[str, Any] | None = None,
        peer_host: str = "127.0.0.1",
    ) -> WebConsoleResponse:
        normalized_method = method.upper().strip()
        path = urlsplit(raw_path).path or "/"
        if peer_host != "127.0.0.1":
            return self._json_response(403, {"error": "loopback peer required"})
        if path == "/health":
            if normalized_method not in {"GET", "HEAD"}:
                return self._json_response(405, {"error": "method not allowed"})
            response = self._json_response(
                200,
                {
                    "ai_authority": "advisory-only",
                    "calculation_authority": "Deterministic Engine",
                    "correlation_id": self._snapshot.correlation_id,
                    "evidence_authority": "Registered Evidence",
                    "host_scope": "loopback-only",
                    "mode": "paper-only",
                    "operator_review_required": True,
                    "status": "ok",
                },
            )
            return self._head(response) if normalized_method == "HEAD" else response
        if path == "/api/intake/validate":
            if normalized_method != "POST":
                return self._json_response(405, {"error": "method not allowed"})
            try:
                receipt = self._intake.validate(payload or {}, peer_host)
            except ValueError as exc:
                return self._json_response(
                    400,
                    {"error": str(exc), "status": "BLOCKED"},
                )
            return self._json_response(200, _receipt_payload(receipt))
        if path in {"/api/conversation/request", "/api/operator/request"}:
            if normalized_method != "POST":
                return self._json_response(405, {"error": "method not allowed"})
            try:
                receipt = self._actions.validate(payload or {}, peer_host)
            except ValueError as exc:
                return self._json_response(
                    400,
                    {"error": str(exc), "status": "BLOCKED"},
                )
            return self._json_response(200, _receipt_payload(receipt))
        route = next(
            (candidate for candidate in FCF_WEB_CONSOLE_ROUTES if candidate.path == path),
            None,
        )
        if route is None:
            return self._json_response(404, {"error": "not found"})
        if normalized_method not in {"GET", "HEAD"}:
            return self._json_response(405, {"error": "method not allowed"})
        response = WebConsoleResponse(
            status=200,
            content_type="text/html; charset=utf-8",
            body=self._layout(route.path, route.title, self._page(route.path)),
        )
        return self._head(response) if normalized_method == "HEAD" else response

    def _json_response(
        self,
        status: int,
        payload: Mapping[str, Any],
    ) -> WebConsoleResponse:
        return WebConsoleResponse(
            status=status,
            content_type="application/json; charset=utf-8",
            body=_json_bytes(payload),
        )

    @staticmethod
    def _head(response: WebConsoleResponse) -> WebConsoleResponse:
        return WebConsoleResponse(
            status=response.status,
            content_type=response.content_type,
            body=b"",
            headers=response.headers,
        )

    def _layout(self, active_path: str, title: str, body: str) -> bytes:
        navigation = "".join(
            (
                f'<a class="{"active" if route.path == active_path else ""}" '
                f'href="{route.path}">{_escape(route.title)}</a>'
            )
            for route in FCF_WEB_CONSOLE_ROUTES
        )
        document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FCF | {_escape(title)}</title>
<style>
:root{{--ink:#10222c;--muted:#60727c;--paper:#f3f0e8;--card:#fffdf7;
--nav:#102b33;--accent:#b76535;--safe:#176b55;--risk:#a53f3f;--line:#d8d3c7}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);
font-family:Inter,Segoe UI,Arial,sans-serif}}header{{padding:24px 30px;background:var(--nav);
color:white;display:flex;justify-content:space-between;gap:20px;align-items:center}}
header h1{{margin:0;font-size:22px;letter-spacing:.04em}}header p{{margin:5px 0 0;color:#c7d4d7}}
.status{{border:1px solid #5e7b82;border-radius:99px;padding:8px 12px;font-size:12px}}
.shell{{display:grid;grid-template-columns:230px 1fr;min-height:calc(100vh - 91px)}}
nav{{padding:22px 14px;background:#173740}}nav a{{display:block;color:#d5e0e2;
text-decoration:none;padding:10px 12px;margin:2px 0;border-radius:7px;font-size:14px}}
nav a:hover,nav a.active{{background:#28515b;color:white}}main{{padding:28px;max-width:1480px}}
.eyebrow{{text-transform:uppercase;letter-spacing:.16em;color:var(--accent);
font-size:12px;font-weight:700}}h2{{font-size:30px;margin:8px 0 20px}}h3{{margin-top:0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:15px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;
padding:18px;box-shadow:0 4px 16px rgba(16,34,44,.05);margin-bottom:15px}}
.metric strong{{display:block;font-size:25px;margin:8px 0}}.muted{{color:var(--muted)}}
.good{{color:var(--safe)}}.warn{{color:var(--risk)}}.badge{{display:inline-block;
border-radius:99px;background:#e5ebe7;padding:4px 8px;font-size:11px;margin:2px}}
label{{display:block;font-size:13px;font-weight:650;margin:12px 0 5px}}
input,textarea,select,button{{font:inherit}}input,textarea,select{{width:100%;padding:10px;
border:1px solid #c7c2b7;border-radius:7px;background:white}}textarea{{min-height:110px}}
button{{border:0;border-radius:7px;background:var(--accent);color:white;padding:10px 15px;
cursor:pointer;margin:8px 6px 0 0}}button.secondary{{background:#42646d}}
.notice{{border-left:4px solid var(--accent);background:#fff6e9;padding:13px;margin:15px 0}}
.result{{white-space:pre-wrap;overflow-wrap:anywhere;background:#edf1ed;padding:12px;
border-radius:7px;min-height:42px}}table{{width:100%;border-collapse:collapse}}
th,td{{text-align:left;border-bottom:1px solid var(--line);padding:9px;vertical-align:top}}
code{{white-space:pre-wrap;overflow-wrap:anywhere}}@media(max-width:800px){{
.shell{{grid-template-columns:1fr}}nav{{display:flex;overflow:auto;padding:10px}}
nav a{{white-space:nowrap}}main{{padding:18px}}header{{align-items:flex-start;flex-direction:column}}}}
</style>
</head>
<body>
<header><div><h1>Financial Cognitive Framework</h1>
<p>Research operating console / deterministic authority / registered evidence</p></div>
<div class="status">PAPER ONLY &middot; LOOPBACK &middot; OPERATOR REVIEW</div></header>
<div class="shell"><nav>{navigation}</nav><main>
<div class="eyebrow">FCF Web Console Stage 8</div>
<h2>{_escape(title)}</h2>
{body}
<div class="notice">No control on this screen can place an order, connect an
account, approve itself, change deterministic calculations, or make unregistered
input authoritative.</div>
</main></div>
<script>
const fcfId = prefix => prefix + "-" + Date.now().toString(36);
const fcfDigest = async bytes => Array.from(
  new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))
).map(value => value.toString(16).padStart(2, "0")).join("");
const fcfPost = async (endpoint, payload, output) => {{
  output.textContent = "Validating governed request...";
  try {{
    const response = await fetch(endpoint, {{
      method: "POST",
      headers: {{"Content-Type": "application/json"}},
      body: JSON.stringify(payload)
    }});
    const body = await response.json();
    output.textContent = JSON.stringify(body, null, 2);
  }} catch (error) {{
    output.textContent = "Local request failed: " + error.message;
  }}
}};
const intakeForm = document.getElementById("intake-form");
if (intakeForm) intakeForm.addEventListener("submit", async event => {{
  event.preventDefault();
  const items = [];
  const kindFor = name => {{
    const extension = name.toLowerCase().split(".").pop();
    if (extension === "pdf") return "PDF";
    if (extension === "xlsx" || extension === "xls") return "EXCEL";
    if (extension === "csv") return "CSV";
    if (extension === "json") return "JSON";
    return "LOCAL_FILE";
  }};
  for (const file of document.getElementById("intake-files").files) {{
    items.push({{
      item_id: fcfId("file"),
      kind: kindFor(file.name),
      display_name: file.name,
      media_type: file.type || "application/octet-stream",
      size_bytes: file.size,
      content_sha256: await fcfDigest(await file.arrayBuffer()),
      source_reference: ""
    }});
  }}
  const textValue = document.getElementById("intake-text").value.trim();
  if (textValue) {{
    const bytes = new TextEncoder().encode(textValue);
    items.push({{item_id:fcfId("text"),kind:"TEXT",display_name:"operator-text",
      media_type:"text/plain",size_bytes:bytes.length,
      content_sha256:await fcfDigest(bytes),source_reference:""}});
  }}
  const urlValue = document.getElementById("intake-url").value.trim();
  if (urlValue) {{
    const bytes = new TextEncoder().encode(urlValue);
    items.push({{item_id:fcfId("url"),kind:"URL",display_name:"approved-url",
      media_type:"text/uri-list",size_bytes:bytes.length,
      content_sha256:await fcfDigest(bytes),source_reference:urlValue}});
  }}
  await fcfPost("/api/intake/validate", {{
    request_id:fcfId("intake"),correlation_id:intakeForm.dataset.correlation,
    operator_id:document.getElementById("intake-operator").value,
    confirmed:document.getElementById("intake-confirmed").checked,items,
    source_classification:document.getElementById("source-classification").value,
    trust_classification:document.getElementById("trust-classification").value,
    freshness_classification:document.getElementById("freshness-classification").value,
    licensing_status:document.getElementById("licensing-status").value
  }}, intakeForm.querySelector("[data-result]"));
}});
document.querySelectorAll("[data-action-form]").forEach(form => {{
  form.addEventListener("submit", async event => {{
    event.preventDefault();
    await fcfPost(form.dataset.endpoint || "/api/operator/request", {{
      request_id:fcfId("action"),correlation_id:form.dataset.correlation,
      operator_id:form.querySelector("[name=operator_id]").value,
      action:form.querySelector("[name=action]").value,
      target_artifact_id:form.querySelector("[name=target_artifact_id]").value,
      reason:form.querySelector("[name=reason]").value,
      confirmed:form.querySelector("[name=confirmed]").checked
    }}, form.querySelector("[data-result]"));
  }});
}});
</script>
</body></html>"""
        return document.encode("utf-8")

    def _page(self, path: str) -> str:
        builders = {
            "/": self._overview,
            "/intake": self._intake_page,
            "/conversation": self._conversation_page,
            "/workflows": lambda: self._artifact_page(
                (
                    "research_run",
                    "workflow_status",
                    "runtime_health",
                    "runtime_cost",
                    "degradation",
                )
            ),
            "/evidence": lambda: self._artifact_page(tuple(self._snapshot.sections)),
            "/models": lambda: self._artifact_page(
                ("ai_explanation", "ai_evaluation", "model_comparison", "disagreement")
            ),
            "/risk": lambda: self._artifact_page(
                ("risk_flags", "ranked_watchlist", "policy_snapshot", "contradiction")
            ),
            "/portfolio": lambda: self._artifact_page(
                (
                    "portfolio_construction",
                    "portfolio_construction_outcome",
                    "portfolio_stress",
                    "stress_scenario",
                    "multi_market_validation",
                )
            ),
            "/paper-portfolio": lambda: self._artifact_page(
                (
                    "paper_position",
                    "paper_position_proposal",
                    "paper_validation",
                    "paper_portfolio_validation",
                    "shadow_market_observation",
                )
            ),
            "/reports": lambda: self._artifact_page(
                ("comprehensive_report", "report_archive", "audit_receipt")
            ),
            "/operator-review": self._operator_page,
            "/operations": self._operations_page,
        }
        return builders[path]()

    def _overview(self) -> str:
        failures = len(self._snapshot.sections.get("failure", ()))
        degraded = len(self._snapshot.sections.get("degradation", ()))
        costs = len(self._snapshot.sections.get("runtime_cost", ()))
        return f"""
<div class="grid">
<section class="card metric"><span class="muted">Registered artifacts</span>
<strong>{len(self._snapshot.source_artifact_ids)}</strong>
<span class="good">Registered Evidence authority</span></section>
<section class="card metric"><span class="muted">Workflow failures</span>
<strong>{failures}</strong><span class="{'good' if failures == 0 else 'warn'}">Visible and fail-closed</span></section>
<section class="card metric"><span class="muted">Degradation records</span>
<strong>{degraded}</strong><span class="muted">Never hidden</span></section>
<section class="card metric"><span class="muted">Cost records</span>
<strong>{costs}</strong><span class="muted">Governed runtime accounting</span></section>
</div>
<section class="card"><h3>Authority map</h3><table>
<tr><th>Domain</th><th>Authority</th><th>Console role</th></tr>
<tr><td>Calculations</td><td>Deterministic Engine</td><td>Present only</td></tr>
<tr><td>Evidence</td><td>Registered Evidence</td><td>Inspect and reference</td></tr>
<tr><td>AI</td><td>Advisory only</td><td>Compare with disagreement visible</td></tr>
<tr><td>Decision</td><td>Operator</td><td>Validate explicit governed requests</td></tr>
</table></section>
<section class="card"><h3>Correlation</h3><code>{_escape(self._snapshot.correlation_id)}</code></section>
"""

    def _intake_page(self) -> str:
        return f"""
<form id="intake-form" class="card" data-correlation="{_escape(self._snapshot.correlation_id)}">
<h3>File and data intake</h3>
<p class="muted">PDF, Excel, CSV, JSON, text, approved HTTPS URL, local-file
selection, and multi-file requests are quarantined pending evidence registration.</p>
<label>Files (multiple allowed)</label>
<input id="intake-files" type="file" multiple accept=".pdf,.xlsx,.xls,.csv,.json,.txt">
<label>Text input</label><textarea id="intake-text" placeholder="Paste research evidence text"></textarea>
<label>Approved URL</label><input id="intake-url" type="url" placeholder="https://approved.example/evidence">
<div class="grid"><div><label>Source classification</label>
<select id="source-classification"><option>CLASS_A</option><option>CLASS_B</option><option>CLASS_C</option></select></div>
<div><label>Trust classification</label><select id="trust-classification"><option>UNTRUSTED</option>
<option>REVIEWED_SOURCE</option></select></div><div><label>Freshness</label>
<select id="freshness-classification"><option>REQUIRES_CHECK</option><option>CURRENT</option><option>STALE</option></select></div>
<div><label>Licensing</label><select id="licensing-status"><option>REQUIRES_REVIEW</option>
<option>PERMITTED_READ_ONLY</option></select></div></div>
<label>Operator identity</label><input id="intake-operator" required placeholder="operator-id">
<label><input id="intake-confirmed" type="checkbox" style="width:auto"> Explicit confirmation</label>
<button type="submit">Validate intake request</button>
<pre class="result" data-result>No bytes are authoritative until an approved evidence workflow
completes format validation, quarantine, credential and privacy checks,
normalization, checksum verification, registration, licensing, and quality gates.
</pre></form>"""

    def _conversation_page(self) -> str:
        return f"""
<form class="card" data-action-form data-endpoint="/api/conversation/request"
data-correlation="{_escape(self._snapshot.correlation_id)}"><h3>Controlled research request</h3>
<input type="hidden" name="action" value="ASK_RESEARCH_QUESTION">
<label>Registered artifact target</label><input name="target_artifact_id" required placeholder="artifact-id">
<label>Approved runtime mode</label><select><option>HYBRID</option>
<option>LOCAL_ONLY</option><option>REGISTERED_RESULT_COMPARISON</option></select>
<label>Question or explanation request</label>
<textarea name="reason" required placeholder="Ask about registered evidence or request a comparison"></textarea>
<label>Operator identity</label><input name="operator_id" required placeholder="operator-id">
<label><input name="confirmed" type="checkbox" style="width:auto"> Explicit confirmation</label>
<button type="submit">Submit governed research request</button>
<pre class="result" data-result>The request cannot invoke a model in Stage 8, bypass policy,
change scores or weights, remove risks, authorize archives, or create orders.
</pre></form>"""

    def _operator_page(self) -> str:
        actions = (
            "Approve for Research Archive",
            "Reject",
            "Request Re-analysis",
            "Request More Evidence",
            "Mark Data as Untrusted",
            "Compare Models",
            "Override with Reason",
            "Freeze Report",
            "Export",
            "Stop Workflow",
        )
        action_values = (
            "APPROVE_FOR_RESEARCH_ARCHIVE",
            "REJECT",
            "REQUEST_REANALYSIS",
            "REQUEST_MORE_EVIDENCE",
            "MARK_DATA_UNTRUSTED",
            "COMPARE_MODELS",
            "OVERRIDE_WITH_REASON",
            "FREEZE_REPORT",
            "EXPORT",
            "STOP_WORKFLOW",
        )
        options = "".join(
            f'<option value="{value}">{_escape(label)}</option>'
            for label, value in zip(actions, action_values)
        )
        return f"""
<form class="card" data-action-form data-correlation="{_escape(self._snapshot.correlation_id)}">
<h3>Explicit Operator request</h3>
<label>Action</label><select name="action">{options}</select>
<label>Target registered artifact</label><input name="target_artifact_id" required placeholder="artifact-id">
<label>Operator identity</label><input name="operator_id" required placeholder="operator-id">
<label>Reason</label><textarea name="reason" required placeholder="Required reason and review context"></textarea>
<label><input name="confirmed" type="checkbox" style="width:auto"> Confirm this governed request</label>
<button type="submit">Validate request</button>
<pre class="result" data-result>Validation creates an auditable request receipt only. It does
not approve, reject, archive, freeze, export, override, or transition anything.
</pre></form>"""

    def _operations_page(self) -> str:
        correlation = _escape(self._snapshot.correlation_id)
        return f"""
<div class="grid"><form class="card" data-action-form data-correlation="{correlation}"><h3>Start workflow</h3>
<p>Create a reviewed start request against registered inputs.</p>
<input type="hidden" name="action" value="START_WORKFLOW">
<input name="target_artifact_id" required placeholder="registered-workflow-id">
<input name="operator_id" required placeholder="operator-id">
<textarea name="reason" required placeholder="Required start reason"></textarea>
<label><input name="confirmed" type="checkbox" style="width:auto"> Confirm</label>
<button type="submit">Request Start</button><pre class="result" data-result></pre></form>
<form class="card" data-action-form data-correlation="{correlation}">
<h3>Stop workflow</h3><p>Create a reviewed cancellation request. Failures and
partial degradation remain visible.</p>
<input type="hidden" name="action" value="STOP_WORKFLOW">
<input name="target_artifact_id" required placeholder="registered-workflow-id">
<input name="operator_id" required placeholder="operator-id">
<textarea name="reason" required placeholder="Required stop reason"></textarea>
<label><input name="confirmed" type="checkbox" style="width:auto"> Confirm</label>
<button type="submit" class="secondary">Request Stop</button>
<pre class="result" data-result></pre></form></div><section class="card"><h3>Lifecycle boundary</h3>
<p>Stage 8 supplies one-click request controls. Local process startup, shutdown,
health supervision, and nontechnical launcher packaging are delivered by the
separately governed ONE-CLICK-LOCAL-OPERATIONS-APP-1 stage.</p></section>"""

    def _artifact_page(self, artifact_types: Tuple[str, ...]) -> str:
        cards = []
        for artifact_type in artifact_types:
            for payload in self._snapshot.sections.get(artifact_type, ()):
                serialized = json.dumps(
                    dict(payload),
                    ensure_ascii=True,
                    indent=2,
                    sort_keys=True,
                )
                cards.append(
                    '<section class="card">'
                    f"<h3>{_escape(artifact_type)}</h3>"
                    f"<code>{_escape(serialized)}</code></section>"
                )
        if not cards:
            return (
                '<section class="card"><h3>No registered evidence</h3>'
                '<p class="muted">This view fails closed and never substitutes '
                "unregistered input.</p></section>"
            )
        return "".join(cards)
