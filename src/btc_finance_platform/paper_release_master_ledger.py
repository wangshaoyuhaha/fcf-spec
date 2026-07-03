from __future__ import annotations

from typing import Any


def build_paper_release_master_ledger() -> dict[str, Any]:
    phases = [
        {"phase": "P14", "title": "Learning Engine Paper Release", "status": "RELEASED"},
        {"phase": "P15", "title": "Post Release Continuity Pack", "status": "COMPLETED"},
        {"phase": "P16", "title": "Operator Evidence Console", "status": "COMPLETED"},
        {"phase": "P17", "title": "Local Evidence Export Files", "status": "COMPLETED"},
        {"phase": "P18", "title": "Local Evidence Navigation", "status": "COMPLETED"},
        {"phase": "P19", "title": "Local Evidence Archive View", "status": "COMPLETED"},
        {"phase": "P20", "title": "Local Evidence Final Review", "status": "COMPLETED"},
        {"phase": "P21", "title": "Paper Evidence Master Closeout", "status": "COMPLETED"},
    ]
    return {
        "ok": True,
        "type": "paper_release_master_ledger",
        "phase": "P22-D1-D3",
        "release_tag": "v14-learning-engine-paper",
        "ledger_entries": phases,
        "entry_count": len(phases),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def summarize_paper_release_master_ledger() -> dict[str, Any]:
    ledger = build_paper_release_master_ledger()
    completed_or_released = [
        item for item in ledger["ledger_entries"]
        if item["status"] in {"COMPLETED", "RELEASED"}
    ]
    return {
        "ok": len(completed_or_released) == ledger["entry_count"],
        "type": "paper_release_master_ledger_summary",
        "release_tag": ledger["release_tag"],
        "entry_count": ledger["entry_count"],
        "completed_or_released_count": len(completed_or_released),
        "latest_phase": ledger["ledger_entries"][-1]["phase"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def evaluate_paper_release_master_ledger_safety() -> dict[str, Any]:
    ledger = build_paper_release_master_ledger()
    summary = summarize_paper_release_master_ledger()
    passed = (
        ledger["paper_only"] is True
        and ledger["local_only"] is True
        and ledger["read_only"] is True
        and ledger["deploy_enabled"] is False
        and ledger["real_trading_enabled"] is False
        and ledger["operator_review_required"] is True
        and summary["ok"] is True
    )
    return {
        "ok": passed,
        "type": "paper_release_master_ledger_safety_gate",
        "status": "PASSED" if passed else "FAILED",
        "entry_count": ledger["entry_count"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "real_money_impact": False,
        "operator_review_required": True,
    }
