import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_governance_audit import build_governance_audit_trail


PAPER_ONLY_FLAGS = {
    "paper_only": True,
    "real_exchange_api": False,
    "real_api_key_required": False,
    "wallet_private_key_required": False,
    "real_order": False,
    "real_execution": False,
    "real_balance": False,
    "real_position": False,
    "real_money_impact": False,
    "operator_review_required": True,
}


def paper_flags() -> dict[str, Any]:
    return dict(PAPER_ONLY_FLAGS)


def require_governance_audit_trail(trail: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(trail, dict):
        raise ValueError("governance_audit_trail must be a dict")
    if trail.get("ok") is not True:
        raise ValueError("governance_audit_trail must be ok")
    if trail.get("type") != "governance_audit_trail":
        raise ValueError("governance_audit_trail type is invalid")
    return trail


def build_governance_report_summary(
    file_paths: list[Any],
    operator_status: str = "pending",
) -> dict[str, Any]:
    trail = build_governance_audit_trail(file_paths, operator_status)
    trail = require_governance_audit_trail(trail)
    report = trail["governance_report"]

    return {
        "ok": True,
        "type": "governance_report_summary",
        "count": report["count"],
        "event_count": trail["event_count"],
        "symbols": report["symbols"],
        "gate_counts": report["gate_counts"],
        "regime_counts": report["regime_counts"],
        "constraint_summary": trail["constraint_summary"],
        "operator_gate": trail["operator_gate"],
        "decision": "governance_summary_paper_only",
        **paper_flags(),
    }


def build_governance_symbol_markdown_section(
    governor_decision: dict[str, Any],
    policy_gate: dict[str, Any],
) -> str:
    if not isinstance(governor_decision, dict):
        raise ValueError("governor_decision must be a dict")
    if not isinstance(policy_gate, dict):
        raise ValueError("policy_gate must be a dict")

    lines = [
        "### " + str(governor_decision["symbol"]),
        "",
        "- Governor gate: " + str(governor_decision["gate"]),
        "- Allowed action: " + str(governor_decision["allowed_action"]),
        "- Risk level: " + str(governor_decision["risk_level"]),
        "- Risk score: " + str(governor_decision["risk_score"]),
        "- Signal: " + str(governor_decision["signal"]),
        "- Regime: " + str(governor_decision["regime"]["regime"]),
        "- Policy gate: " + str(policy_gate["gate"]),
        "- Policy approved action: " + str(policy_gate["approved_action"]),
        "- Decision: " + str(governor_decision["decision"]),
        "",
        "Blocked reasons:",
    ]

    if governor_decision["blocked_reasons"]:
        for reason in governor_decision["blocked_reasons"]:
            lines.append("- " + str(reason))
    else:
        lines.append("- none")

    lines.extend([
        "",
        "Warnings:",
    ])

    if governor_decision["warnings"]:
        for warning in governor_decision["warnings"]:
            lines.append("- " + str(warning))
    else:
        lines.append("- none")

    lines.append("")
    return "\n".join(lines)


def build_governance_markdown_report(
    file_paths: list[Any],
    operator_status: str = "pending",
) -> dict[str, Any]:
    trail = build_governance_audit_trail(file_paths, operator_status)
    trail = require_governance_audit_trail(trail)
    summary = build_governance_report_summary(file_paths, operator_status)
    report = trail["governance_report"]

    lines = [
        "# Paper Governance Report",
        "",
        "Status: paper-only governance report",
        "",
        "Created at UTC: " + datetime.now(timezone.utc).isoformat(),
        "",
        "## Safety Boundary",
        "",
        "- Paper-only: true",
        "- Real exchange API: false",
        "- Real API key required: false",
        "- Wallet private key required: false",
        "- Real order: false",
        "- Real execution: false",
        "- Real balance: false",
        "- Real position: false",
        "- Real money impact: false",
        "- Operator review required: true",
        "",
        "## Summary",
        "",
        "- Count: " + str(summary["count"]),
        "- Event count: " + str(summary["event_count"]),
        "- Symbols: " + ", ".join(summary["symbols"]),
        "- Gate counts: " + json.dumps(summary["gate_counts"], sort_keys=True),
        "- Regime counts: " + json.dumps(summary["regime_counts"], sort_keys=True),
        "- Operator gate: " + str(summary["operator_gate"]["gate"]),
        "- Operator allowed action: " + str(summary["operator_gate"]["allowed_action"]),
        "",
        "## Policy Constraints",
        "",
        "- Required review: " + str(summary["constraint_summary"]["required_review"]),
        "- Failed gate count: " + str(summary["constraint_summary"]["failed_gate_count"]),
        "- Blocked actions: " + ", ".join(summary["constraint_summary"]["blocked_actions"]),
        "",
        "## Symbol Governance Items",
        "",
    ]

    for governor_decision, policy_gate in zip(
        report["governor_decisions"],
        report["policy_gates"],
    ):
        lines.append(build_governance_symbol_markdown_section(
            governor_decision,
            policy_gate,
        ))

    lines.extend([
        "## Final Notice",
        "",
        "This governance report is not financial advice.",
        "This governance report is not a real trading signal.",
        "This governance report must not be used for real execution.",
        "Operator approval still does not permit real-world trading actions.",
        "",
    ])

    markdown = "\n".join(lines)

    return {
        "ok": True,
        "type": "governance_markdown_report",
        "summary": summary,
        "markdown": markdown,
        "audit_trail": trail,
        "decision": "governance_markdown_report_paper_only",
        **paper_flags(),
    }


def write_governance_report_bundle(
    file_paths: list[Any],
    output_dir: Any,
    operator_status: str = "pending",
) -> dict[str, Any]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    report = build_governance_markdown_report(file_paths, operator_status)
    markdown_path = directory / "paper_governance_report.md"
    json_path = directory / "paper_governance_report.json"

    markdown_path.write_text(report["markdown"], encoding="utf-8")
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "governance_report_bundle_written",
        "output_dir": str(directory),
        "markdown_file": str(markdown_path),
        "json_file": str(json_path),
        "report": report,
        **paper_flags(),
    }
