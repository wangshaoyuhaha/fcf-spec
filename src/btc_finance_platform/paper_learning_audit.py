import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_learning_memory import (
    build_operator_feedback_dataset,
    build_paper_outcome_tracking_contract,
)

PAPER_ONLY_FLAGS = {
    "paper_only": True,
    "real_exchange_api": False,
    "real_brokerage_api": False,
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


def build_learning_audit_event(symbol: str, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    if not symbol or not str(symbol).strip():
        raise ValueError("symbol is required")
    if not event_type or not str(event_type).strip():
        raise ValueError("event_type is required")
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")

    return {
        "ok": True,
        "type": "learning_audit_event",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": str(symbol).strip().upper(),
        "event_type": str(event_type).strip(),
        "payload": payload,
        "real_world_actions_allowed": False,
        "decision": "learning_audit_event_paper_only",
        **paper_flags(),
    }


def build_learning_event_audit_trail(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    dataset = build_operator_feedback_dataset(file_path, action_by_symbol, outcome_by_symbol)
    tracking = build_paper_outcome_tracking_contract(file_path, action_by_symbol, outcome_by_symbol)

    events = []
    for record in dataset["records"]:
        events.append(build_learning_audit_event(record["symbol"], "learning_memory_recorded", record))
    for item in tracking["items"]:
        events.append(build_learning_audit_event(item["symbol"], "paper_outcome_tracked", item))

    return {
        "ok": all(event["ok"] for event in events),
        "type": "learning_event_audit_trail",
        "audit_version": "p8_d4_learning_event_audit_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "event_count": len(events),
        "symbols": dataset["symbols"],
        "events": events,
        "source_dataset": dataset,
        "source_tracking": tracking,
        "decision": "learning_event_audit_trail_paper_only",
        **paper_flags(),
    }


def build_feedback_to_calibration_handoff(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    dataset = build_operator_feedback_dataset(file_path, action_by_symbol, outcome_by_symbol)

    rows = []
    for record in dataset["records"]:
        rows.append({
            "symbol": record["symbol"],
            "asset_class": record["asset_class"],
            "market": record["market"],
            "paper_signal": record["paper_signal"],
            "risk_level": record["risk_level"],
            "risk_score": record["risk_score"],
            "operator_action": record["operator_action"],
            "paper_outcome_status": record["paper_outcome_status"],
            "calibration_use": "future_offline_backtest_and_calibration_only",
            "real_world_actions_allowed": False,
        })

    return {
        "ok": True,
        "type": "feedback_to_calibration_handoff",
        "handoff_version": "p8_d5_feedback_to_calibration_handoff_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "count": len(rows),
        "symbols": [row["symbol"] for row in rows],
        "action_counts": dataset["action_counts"],
        "outcome_counts": dataset["outcome_counts"],
        "risk_counts": dataset["risk_counts"],
        "rows": rows,
        "next_phase": "P9 backtest and calibration",
        "training_status": "not_trained_not_calibrated_yet",
        "decision": "feedback_handoff_paper_only_no_training_now",
        **paper_flags(),
    }


def build_learning_memory_summary(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    audit = build_learning_event_audit_trail(file_path, action_by_symbol, outcome_by_symbol)
    handoff = build_feedback_to_calibration_handoff(file_path, action_by_symbol, outcome_by_symbol)

    return {
        "ok": audit["ok"] is True and handoff["ok"] is True,
        "type": "learning_memory_summary",
        "source_file": str(Path(file_path).name),
        "event_count": audit["event_count"],
        "handoff_count": handoff["count"],
        "symbols": handoff["symbols"],
        "action_counts": handoff["action_counts"],
        "outcome_counts": handoff["outcome_counts"],
        "risk_counts": handoff["risk_counts"],
        "next_phase": handoff["next_phase"],
        "training_status": handoff["training_status"],
        "real_world_actions_allowed": False,
        "decision": "learning_memory_summary_paper_only",
        **paper_flags(),
    }


def build_learning_memory_markdown_report(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    summary = build_learning_memory_summary(file_path, action_by_symbol, outcome_by_symbol)
    handoff = build_feedback_to_calibration_handoff(file_path, action_by_symbol, outcome_by_symbol)

    lines = [
        "# Paper Learning Memory Report",
        "",
        "Status: paper-only learning memory report",
        "",
        "## Safety Boundary",
        "",
        "- Paper-only: true",
        "- Real exchange API: false",
        "- Real brokerage API: false",
        "- Real order: false",
        "- Real execution: false",
        "- Real money impact: false",
        "- Operator review required: true",
        "",
        "## Summary",
        "",
        "- Event count: " + str(summary["event_count"]),
        "- Handoff count: " + str(summary["handoff_count"]),
        "- Symbols: " + ", ".join(summary["symbols"]),
        "- Action counts: " + json.dumps(summary["action_counts"], sort_keys=True),
        "- Outcome counts: " + json.dumps(summary["outcome_counts"], sort_keys=True),
        "- Risk counts: " + json.dumps(summary["risk_counts"], sort_keys=True),
        "- Training status: " + summary["training_status"],
        "- Next phase: " + summary["next_phase"],
        "",
        "## Final Notice",
        "",
        "This report does not train a model.",
        "This report does not calibrate a strategy yet.",
        "This report must not be used for real execution.",
        "",
    ]

    return {
        "ok": True,
        "type": "learning_memory_markdown_report",
        "summary": summary,
        "handoff": handoff,
        "markdown": "\n".join(lines),
        "decision": "learning_memory_markdown_report_paper_only",
        **paper_flags(),
    }


def write_learning_audit_report_bundle(
    file_path: Any,
    output_dir: Any,
    action_by_symbol: dict[str, str] | None = None,
    outcome_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    audit = build_learning_event_audit_trail(file_path, action_by_symbol, outcome_by_symbol)
    handoff = build_feedback_to_calibration_handoff(file_path, action_by_symbol, outcome_by_symbol)
    report = build_learning_memory_markdown_report(file_path, action_by_symbol, outcome_by_symbol)

    audit_path = directory / "learning_event_audit_trail.json"
    handoff_path = directory / "feedback_to_calibration_handoff.json"
    report_path = directory / "learning_memory_report.md"

    audit_path.write_text(json.dumps(audit, indent=2, sort_keys=True), encoding="utf-8")
    handoff_path.write_text(json.dumps(handoff, indent=2, sort_keys=True), encoding="utf-8")
    report_path.write_text(report["markdown"], encoding="utf-8")

    return {
        "ok": True,
        "type": "learning_audit_report_bundle_written",
        "output_dir": str(directory),
        "audit_file": str(audit_path),
        "handoff_file": str(handoff_path),
        "report_file": str(report_path),
        "audit": audit,
        "handoff": handoff,
        "report": report,
        **paper_flags(),
    }
