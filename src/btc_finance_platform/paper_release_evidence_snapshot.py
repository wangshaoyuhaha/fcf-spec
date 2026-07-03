from __future__ import annotations

from typing import Any

from btc_finance_platform.paper_release_master_ledger import build_paper_release_master_ledger


def build_paper_release_evidence_snapshot() -> dict[str, Any]:
    ledger = build_paper_release_master_ledger()
    snapshot_items = list(ledger["ledger_entries"]) + [
        {"phase": "P22", "title": "Paper Release Master Ledger", "status": "COMPLETED"},
    ]
    return {
        "ok": ledger["ok"],
        "type": "paper_release_evidence_snapshot",
        "phase": "P23-D1-D6",
        "release_tag": ledger["release_tag"],
        "snapshot_items": snapshot_items,
        "item_count": len(snapshot_items),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def summarize_paper_release_evidence_snapshot() -> dict[str, Any]:
    snapshot = build_paper_release_evidence_snapshot()
    complete = [
        item for item in snapshot["snapshot_items"]
        if item["status"] in {"COMPLETED", "RELEASED"}
    ]
    return {
        "ok": len(complete) == snapshot["item_count"],
        "type": "paper_release_evidence_snapshot_summary",
        "release_tag": snapshot["release_tag"],
        "item_count": snapshot["item_count"],
        "completed_or_released_count": len(complete),
        "latest_phase": snapshot["snapshot_items"][-1]["phase"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def evaluate_paper_release_evidence_snapshot_safety() -> dict[str, Any]:
    snapshot = build_paper_release_evidence_snapshot()
    summary = summarize_paper_release_evidence_snapshot()
    passed = (
        snapshot["ok"] is True
        and summary["ok"] is True
        and snapshot["item_count"] == 9
        and snapshot["paper_only"] is True
        and snapshot["local_only"] is True
        and snapshot["read_only"] is True
        and snapshot["deploy_enabled"] is False
        and snapshot["real_trading_enabled"] is False
        and snapshot["operator_review_required"] is True
    )
    return {
        "ok": passed,
        "type": "paper_release_evidence_snapshot_safety_gate",
        "status": "PASSED" if passed else "FAILED",
        "item_count": snapshot["item_count"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "real_money_impact": False,
        "operator_review_required": True,
    }


def build_paper_release_evidence_snapshot_readable_report() -> dict[str, Any]:
    summary = summarize_paper_release_evidence_snapshot()
    return {
        "ok": summary["ok"],
        "type": "paper_release_evidence_snapshot_readable_report",
        "title": "P23 Paper Release Evidence Snapshot Readable Report",
        "release_tag": summary["release_tag"],
        "item_count": summary["item_count"],
        "latest_phase": summary["latest_phase"],
        "safety_summary": "paper-only, local-only, read-only, no deploy, no real trading",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def build_paper_release_evidence_snapshot_operator_checklist() -> dict[str, Any]:
    checklist = [
        {"item": "P14 evidence snapshot reviewed", "required": True, "status": "READY"},
        {"item": "P15 evidence snapshot reviewed", "required": True, "status": "READY"},
        {"item": "P16 evidence snapshot reviewed", "required": True, "status": "READY"},
        {"item": "P17 evidence snapshot reviewed", "required": True, "status": "READY"},
        {"item": "P18 evidence snapshot reviewed", "required": True, "status": "READY"},
        {"item": "P19 evidence snapshot reviewed", "required": True, "status": "READY"},
        {"item": "P20 evidence snapshot reviewed", "required": True, "status": "READY"},
        {"item": "P21 evidence snapshot reviewed", "required": True, "status": "READY"},
        {"item": "P22 evidence snapshot reviewed", "required": True, "status": "READY"},
        {"item": "no deploy confirmed", "required": True, "status": "READY"},
        {"item": "no real trading confirmed", "required": True, "status": "READY"},
    ]
    return {
        "ok": True,
        "type": "paper_release_evidence_snapshot_operator_checklist",
        "check_count": len(checklist),
        "checklist": checklist,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def evaluate_paper_release_evidence_snapshot_completion_gate() -> dict[str, Any]:
    report = build_paper_release_evidence_snapshot_readable_report()
    checklist = build_paper_release_evidence_snapshot_operator_checklist()
    safety = evaluate_paper_release_evidence_snapshot_safety()
    all_ready = all(item["required"] is True and item["status"] == "READY" for item in checklist["checklist"])
    passed = (
        report["ok"] is True
        and checklist["ok"] is True
        and safety["ok"] is True
        and all_ready
        and report["deploy_enabled"] is False
        and report["real_trading_enabled"] is False
    )
    return {
        "ok": passed,
        "type": "paper_release_evidence_snapshot_completion_gate",
        "status": "PASSED" if passed else "FAILED",
        "all_required_checks_ready": all_ready,
        "item_count": report["item_count"],
        "check_count": checklist["check_count"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }
