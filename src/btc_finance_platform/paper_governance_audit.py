import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_risk_governance import build_batch_risk_governance_report


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


def require_governance_report(report: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(report, dict):
        raise ValueError("governance_report must be a dict")
    if report.get("ok") is not True:
        raise ValueError("governance_report must be ok")
    if report.get("type") != "batch_risk_governance_report":
        raise ValueError("governance_report type is invalid")
    return report


def build_governance_audit_event(
    symbol: str,
    event_type: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    if not symbol or not str(symbol).strip():
        raise ValueError("symbol is required")
    if not event_type or not str(event_type).strip():
        raise ValueError("event_type is required")
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")

    return {
        "ok": True,
        "type": "governance_audit_event",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": str(symbol).strip().upper(),
        "event_type": str(event_type).strip(),
        "payload": payload,
        "decision": "audit_event_paper_only",
        **paper_flags(),
    }


def build_policy_constraint_summary(
    governance_report: dict[str, Any],
) -> dict[str, Any]:
    report = require_governance_report(governance_report)
    policy_gates = report["policy_gates"]

    blocked_action_counts: dict[str, int] = {}
    failed_gate_count = 0

    for gate in policy_gates:
        if gate["gate"] != "pass":
            failed_gate_count += 1
        for action in gate["blocked_real_world_actions"]:
            blocked_action_counts[action] = blocked_action_counts.get(action, 0) + 1

    return {
        "ok": True,
        "type": "policy_constraint_summary",
        "count": report["count"],
        "symbols": report["symbols"],
        "failed_gate_count": failed_gate_count,
        "blocked_action_counts": blocked_action_counts,
        "blocked_actions": sorted(blocked_action_counts.keys()),
        "required_review": "operator_review_required_for_all_items",
        "decision": "constraints_summary_paper_only",
        **paper_flags(),
    }


def build_operator_approval_gate(
    governance_report: dict[str, Any],
    operator_status: str = "pending",
) -> dict[str, Any]:
    report = require_governance_report(governance_report)
    status = str(operator_status).strip().lower()

    if status not in {"pending", "approved", "rejected"}:
        raise ValueError("operator_status must be pending, approved, or rejected")

    all_policy_gates_pass = all(gate["gate"] == "pass" for gate in report["policy_gates"])

    if status == "approved" and all_policy_gates_pass:
        gate = "paper_review_approved"
        allowed_action = "paper_report_archive_only"
    elif status == "rejected":
        gate = "operator_rejected"
        allowed_action = "paper_review_rejected_archive_only"
    else:
        gate = "operator_review_pending"
        allowed_action = "wait_for_operator_review"

    return {
        "ok": True,
        "type": "operator_approval_gate",
        "operator_status": status,
        "gate": gate,
        "allowed_action": allowed_action,
        "all_policy_gates_pass": all_policy_gates_pass,
        "real_world_actions_allowed": False,
        "decision": "operator_gate_paper_only_no_real_trade",
        **paper_flags(),
    }


def build_governance_audit_trail(
    file_paths: list[Any],
    operator_status: str = "pending",
) -> dict[str, Any]:
    governance_report = build_batch_risk_governance_report(file_paths)
    governance_report = require_governance_report(governance_report)
    constraint_summary = build_policy_constraint_summary(governance_report)
    operator_gate = build_operator_approval_gate(governance_report, operator_status)

    events = []
    for decision in governance_report["governor_decisions"]:
        events.append(build_governance_audit_event(
            decision["symbol"],
            "risk_governor_decision_recorded",
            decision,
        ))

    for gate in governance_report["policy_gates"]:
        events.append(build_governance_audit_event(
            gate["symbol"],
            "policy_gate_decision_recorded",
            gate,
        ))

    return {
        "ok": all(event["ok"] for event in events) and constraint_summary["ok"] is True and operator_gate["ok"] is True,
        "type": "governance_audit_trail",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "event_count": len(events),
        "symbols": governance_report["symbols"],
        "events": events,
        "constraint_summary": constraint_summary,
        "operator_gate": operator_gate,
        "governance_report": governance_report,
        "decision": "governance_audit_trail_paper_only",
        **paper_flags(),
    }


def write_governance_audit_trail(
    file_paths: list[Any],
    output_path: Any,
    operator_status: str = "pending",
) -> dict[str, Any]:
    trail = build_governance_audit_trail(file_paths, operator_status)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(trail, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "governance_audit_trail_written",
        "output_file": str(path),
        "trail": trail,
        **paper_flags(),
    }
