"""UI-APP-D5 local read-only HTML and text report artifacts."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any, Mapping


REPORT_SAFETY_FIELDS: dict[str, Any] = {
    "paper_only": True,
    "local_only": True,
    "read_only": True,
    "sidecar_only": True,
    "operator_review_required": True,
    "operator_review_bypass_allowed": False,
    "trade_action_enabled": False,
    "buy_button_enabled": False,
    "sell_button_enabled": False,
    "order_button_enabled": False,
    "network_access_required": False,
    "credential_access_required": False,
    "real_execution_enabled": False,
    "core_mutation_enabled": False,
}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _rows(view_model: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows = view_model.get("rows", [])
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, Mapping)]


def render_read_only_text_report(
    handoff_payload: Mapping[str, Any],
    ranked_watchlist_view_model: Mapping[str, Any],
    panels: Mapping[str, Any],
) -> str:
    """Render a deterministic local text report."""

    rows = _rows(ranked_watchlist_view_model)
    lines = [
        "UI-APP-1 LOCAL READ-ONLY REPORT",
        "stage_id: UI-APP-D5",
        "paper_only: true",
        "local_only: true",
        "read_only: true",
        "sidecar_only: true",
        "operator_review_required: true",
        "trade_action_enabled: false",
        "buy_button_enabled: false",
        "sell_button_enabled: false",
        "order_button_enabled: false",
        "",
        "Candidates:",
    ]

    if not rows:
        lines.append("- none")
    else:
        for row in rows:
            symbol = str(row.get("symbol", ""))
            rank = str(row.get("rank", ""))
            score = str(row.get("score", ""))
            reasons = ", ".join(str(item) for item in _as_list(row.get("reason_codes")))
            risks = ", ".join(str(item) for item in _as_list(row.get("risk_flags")))
            lines.append(f"- rank={rank} symbol={symbol} score={score}")
            lines.append(f"  reason_codes={reasons}")
            lines.append(f"  risk_flags={risks}")

    panel_group_id = str(panels.get("panel_group_id", ""))
    lines.extend(
        [
            "",
            f"panel_group_id: {panel_group_id}",
            "operator_note: display only; no trading action is available",
        ]
    )
    return "\n".join(lines) + "\n"


def render_read_only_html_report(
    handoff_payload: Mapping[str, Any],
    ranked_watchlist_view_model: Mapping[str, Any],
    panels: Mapping[str, Any],
) -> str:
    """Render a deterministic local HTML report."""

    rows = _rows(ranked_watchlist_view_model)
    body_rows: list[str] = []

    for row in rows:
        reason_codes = ", ".join(str(item) for item in _as_list(row.get("reason_codes")))
        risk_flags = ", ".join(str(item) for item in _as_list(row.get("risk_flags")))
        body_rows.append(
            "<tr>"
            f"<td>{escape(str(row.get('rank', '')))}</td>"
            f"<td>{escape(str(row.get('symbol', '')))}</td>"
            f"<td>{escape(str(row.get('display_name', '')))}</td>"
            f"<td>{escape(str(row.get('score', '')))}</td>"
            f"<td>{escape(str(row.get('data_quality_state', '')))}</td>"
            f"<td>{escape(str(row.get('confidence_level', '')))}</td>"
            f"<td>{escape(reason_codes)}</td>"
            f"<td>{escape(risk_flags)}</td>"
            "<td>required</td>"
            "</tr>"
        )

    if not body_rows:
        body_rows.append('<tr><td colspan="9">NO_RANKED_WATCHLIST_CANDIDATES</td></tr>')

    panel_group_id = escape(str(panels.get("panel_group_id", "")))

    html_lines = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '  <meta charset="utf-8">',
        "  <title>UI-APP-1 Local Read-Only Report</title>",
        "</head>",
        "<body>",
        "  <h1>UI-APP-1 Local Read-Only Report</h1>",
        "  <section>",
        "    <h2>Safety Boundary</h2>",
        "    <ul>",
        "      <li>paper_only: true</li>",
        "      <li>local_only: true</li>",
        "      <li>read_only: true</li>",
        "      <li>sidecar_only: true</li>",
        "      <li>operator_review_required: true</li>",
        "      <li>trade_action_enabled: false</li>",
        "      <li>buy_button_enabled: false</li>",
        "      <li>sell_button_enabled: false</li>",
        "      <li>order_button_enabled: false</li>",
        "    </ul>",
        "  </section>",
        "  <section>",
        "    <h2>Ranked Watchlist</h2>",
        "    <table>",
        "      <thead>",
        "        <tr>",
        "          <th>Rank</th>",
        "          <th>Symbol</th>",
        "          <th>Name</th>",
        "          <th>Score</th>",
        "          <th>Data Quality</th>",
        "          <th>Confidence</th>",
        "          <th>Reason Codes</th>",
        "          <th>Risk Flags</th>",
        "          <th>Operator Review</th>",
        "        </tr>",
        "      </thead>",
        "      <tbody>",
        *["        " + item for item in body_rows],
        "      </tbody>",
        "    </table>",
        "  </section>",
        "  <section>",
        "    <h2>Panel Group</h2>",
        f"    <p>{panel_group_id}</p>",
        "  </section>",
        "  <section>",
        "    <h2>Operator Note</h2>",
        "    <p>Display only. No trading action is available.</p>",
        "  </section>",
        "</body>",
        "</html>",
    ]
    return "\n".join(html_lines) + "\n"


def build_local_report_artifact(
    handoff_payload: Mapping[str, Any],
    ranked_watchlist_view_model: Mapping[str, Any],
    panels: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a local read-only report artifact bundle."""

    text_report = render_read_only_text_report(
        handoff_payload,
        ranked_watchlist_view_model,
        panels,
    )
    html_report = render_read_only_html_report(
        handoff_payload,
        ranked_watchlist_view_model,
        panels,
    )

    return {
        "artifact_id": "ui_app_1_local_read_only_report",
        "stage_id": "UI-APP-D5",
        **REPORT_SAFETY_FIELDS,
        "formats": ("html", "text", "manifest_json"),
        "html_report": html_report,
        "text_report": text_report,
        "manifest": {
            "artifact_id": "ui_app_1_local_read_only_report",
            "stage_id": "UI-APP-D5",
            **REPORT_SAFETY_FIELDS,
            "candidate_count": len(_rows(ranked_watchlist_view_model)),
            "panel_group_id": panels.get("panel_group_id", ""),
        },
    }


def validate_local_report_artifact(
    artifact: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate local report artifact safety."""

    errors: list[str] = []

    for field, expected in REPORT_SAFETY_FIELDS.items():
        if artifact.get(field) is not expected:
            errors.append(f"artifact_field_mismatch:{field}")

    html_report = artifact.get("html_report", "")
    text_report = artifact.get("text_report", "")
    manifest = artifact.get("manifest", {})

    if not isinstance(html_report, str) or "<html" not in html_report:
        errors.append("html_report_invalid")

    if (
        not isinstance(text_report, str)
        or "UI-APP-1 LOCAL READ-ONLY REPORT" not in text_report
    ):
        errors.append("text_report_invalid")

    if not isinstance(manifest, Mapping):
        errors.append("manifest_invalid")
        manifest = {}

    for field in (
        "trade_action_enabled",
        "buy_button_enabled",
        "sell_button_enabled",
        "order_button_enabled",
        "real_execution_enabled",
        "core_mutation_enabled",
    ):
        if artifact.get(field) is not False:
            errors.append(f"forbidden_enabled:{field}")
        if manifest.get(field) is not False:
            errors.append(f"manifest_forbidden_enabled:{field}")

    return {
        "ok": not errors,
        "errors": errors,
        "artifact_id": artifact.get("artifact_id"),
        "stage_id": artifact.get("stage_id"),
    }


def write_local_report_artifact(
    artifact: Mapping[str, Any],
    output_dir: str | Path,
    basename: str = "ui_app_1_local_read_only_report",
) -> dict[str, Any]:
    """Write local report files to an operator-selected directory."""

    validation = validate_local_report_artifact(artifact)
    if not validation["ok"]:
        raise ValueError("invalid_local_report_artifact:" + ",".join(validation["errors"]))

    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)

    html_path = target / f"{basename}.html"
    text_path = target / f"{basename}.txt"
    manifest_path = target / f"{basename}.manifest.json"

    html_path.write_text(str(artifact["html_report"]), encoding="utf-8")
    text_path.write_text(str(artifact["text_report"]), encoding="utf-8")
    manifest_path.write_text(
        json.dumps(artifact["manifest"], indent=2, sort_keys=True),
        encoding="utf-8",
    )

    return {
        "ok": True,
        "html_path": str(html_path),
        "text_path": str(text_path),
        "manifest_path": str(manifest_path),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
    }
