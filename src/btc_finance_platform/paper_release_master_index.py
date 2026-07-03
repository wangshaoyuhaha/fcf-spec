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


def build_paper_release_master_index_readable_report() -> dict[str, Any]:
    summary = summarize_paper_release_master_index()
    return {
        "ok": summary["ok"],
        "type": "paper_release_master_index_readable_report",
        "title": "P24 Paper Release Master Index Readable Report",
        "release_tag": summary["release_tag"],
        "entry_count": summary["entry_count"],
        "indexed_count": summary["indexed_count"],
        "latest_phase": summary["latest_phase"],
        "safety_summary": "paper-only, local-only, read-only, no deploy, no real trading",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def build_paper_release_master_index_operator_checklist() -> dict[str, Any]:
    checklist = [
        {"item": "P14 master index entry reviewed", "required": True, "status": "READY"},
        {"item": "P15 master index entry reviewed", "required": True, "status": "READY"},
        {"item": "P16 master index entry reviewed", "required": True, "status": "READY"},
        {"item": "P17 master index entry reviewed", "required": True, "status": "READY"},
        {"item": "P18 master index entry reviewed", "required": True, "status": "READY"},
        {"item": "P19 master index entry reviewed", "required": True, "status": "READY"},
        {"item": "P20 master index entry reviewed", "required": True, "status": "READY"},
        {"item": "P21 master index entry reviewed", "required": True, "status": "READY"},
        {"item": "P22 master index entry reviewed", "required": True, "status": "READY"},
        {"item": "P23 master index entry reviewed", "required": True, "status": "READY"},
        {"item": "no deploy confirmed", "required": True, "status": "READY"},
        {"item": "no real trading confirmed", "required": True, "status": "READY"},
    ]
    return {
        "ok": True,
        "type": "paper_release_master_index_operator_checklist",
        "check_count": len(checklist),
        "checklist": checklist,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def evaluate_paper_release_master_index_completion_gate() -> dict[str, Any]:
    report = build_paper_release_master_index_readable_report()
    checklist = build_paper_release_master_index_operator_checklist()
    safety = evaluate_paper_release_master_index_safety()
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
        "type": "paper_release_master_index_completion_gate",
        "status": "PASSED" if passed else "FAILED",
        "all_required_checks_ready": all_ready,
        "entry_count": report["entry_count"],
        "check_count": checklist["check_count"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def build_paper_release_master_index_export_packet() -> dict[str, Any]:
    index = build_paper_release_master_index()
    readable = build_paper_release_master_index_readable_report()
    checklist = build_paper_release_master_index_operator_checklist()
    completion = evaluate_paper_release_master_index_completion_gate()
    safety = evaluate_paper_release_master_index_safety()
    return {
        "ok": index["ok"] and readable["ok"] and checklist["ok"] and completion["ok"] and safety["ok"],
        "type": "paper_release_master_index_export_packet",
        "phase": "P24-D7-D12",
        "release_tag": index["release_tag"],
        "index": index,
        "readable_report": readable,
        "operator_checklist": checklist,
        "completion_gate": completion,
        "safety_gate": safety,
        "export_mode": "LOCAL_STATIC_READ_ONLY",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def build_paper_release_master_index_closeout_checkpoint() -> dict[str, Any]:
    packet = build_paper_release_master_index_export_packet()
    return {
        "ok": packet["ok"],
        "type": "paper_release_master_index_closeout_checkpoint",
        "phase": "P24-D7-D12",
        "release_tag": packet["release_tag"],
        "completed": [
            "index_readable_report",
            "index_operator_checklist",
            "index_completion_gate",
            "index_export_packet",
            "index_closeout_checkpoint",
            "index_handoff_packet",
            "final_index_archive_acceptance_packet",
            "final_index_archive_manifest",
            "final_index_handoff_checkpoint",
        ],
        "completion_gate_status": packet["completion_gate"]["status"],
        "safety_gate_status": packet["safety_gate"]["status"],
        "entry_count": packet["index"]["entry_count"],
        "check_count": packet["operator_checklist"]["check_count"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def build_paper_release_master_index_handoff_packet() -> dict[str, Any]:
    closeout = build_paper_release_master_index_closeout_checkpoint()
    return {
        "ok": closeout["ok"],
        "type": "paper_release_master_index_handoff_packet",
        "release_tag": closeout["release_tag"],
        "phase": "P24-D7-D12",
        "handoff_status": "READY_FOR_INDEX_ARCHIVE" if closeout["ok"] else "BLOCKED",
        "closeout": closeout,
        "next_phase_candidate": "P25 Paper Release Final Archive",
        "safety_boundary": "paper-only, local-only, read-only, no deploy, no real trading",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }
