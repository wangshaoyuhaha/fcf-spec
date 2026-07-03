from __future__ import annotations

from typing import Any

from btc_finance_platform.paper_release_evidence_snapshot import build_paper_release_evidence_snapshot_handoff_packet


def build_paper_release_master_index() -> dict[str, Any]:
    handoff = build_paper_release_evidence_snapshot_handoff_packet()
    entries = [
        {"phase": "P14", "category": "release", "status": "INDEXED"},
        {"phase": "P15", "category": "continuity", "status": "INDEXED"},
        {"phase": "P16", "category": "operator_console", "status": "INDEXED"},
        {"phase": "P17", "category": "export", "status": "INDEXED"},
        {"phase": "P18", "category": "navigation", "status": "INDEXED"},
        {"phase": "P19", "category": "archive_view", "status": "INDEXED"},
        {"phase": "P20", "category": "final_review", "status": "INDEXED"},
        {"phase": "P21", "category": "master_closeout", "status": "INDEXED"},
        {"phase": "P22", "category": "release_ledger", "status": "INDEXED"},
        {"phase": "P23", "category": "evidence_snapshot", "status": "INDEXED"},
    ]
    return {
        "ok": handoff["ok"],
        "type": "paper_release_master_index",
        "phase": "P24-D1-D3",
        "release_tag": handoff["release_tag"],
        "entries": entries,
        "entry_count": len(entries),
        "source_handoff_status": handoff["handoff_status"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def summarize_paper_release_master_index() -> dict[str, Any]:
    index = build_paper_release_master_index()
    indexed = [item for item in index["entries"] if item["status"] == "INDEXED"]
    return {
        "ok": len(indexed) == index["entry_count"],
        "type": "paper_release_master_index_summary",
        "release_tag": index["release_tag"],
        "entry_count": index["entry_count"],
        "indexed_count": len(indexed),
        "latest_phase": index["entries"][-1]["phase"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def evaluate_paper_release_master_index_safety() -> dict[str, Any]:
    index = build_paper_release_master_index()
    summary = summarize_paper_release_master_index()
    passed = (
        index["ok"] is True
        and summary["ok"] is True
        and index["source_handoff_status"] == "READY_FOR_SNAPSHOT_ARCHIVE"
        and index["paper_only"] is True
        and index["local_only"] is True
        and index["read_only"] is True
        and index["deploy_enabled"] is False
        and index["real_trading_enabled"] is False
        and index["operator_review_required"] is True
    )
    return {
        "ok": passed,
        "type": "paper_release_master_index_safety_gate",
        "status": "PASSED" if passed else "FAILED",
        "entry_count": index["entry_count"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "real_money_impact": False,
        "operator_review_required": True,
    }
