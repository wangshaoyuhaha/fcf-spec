from __future__ import annotations

from typing import Any

from btc_finance_platform.paper_release_master_index import build_paper_release_master_index_handoff_packet


def build_paper_release_final_archive_packet() -> dict[str, Any]:
    handoff = build_paper_release_master_index_handoff_packet()
    archive_items = [
        {"phase": "P14", "status": "ARCHIVED"},
        {"phase": "P15", "status": "ARCHIVED"},
        {"phase": "P16", "status": "ARCHIVED"},
        {"phase": "P17", "status": "ARCHIVED"},
        {"phase": "P18", "status": "ARCHIVED"},
        {"phase": "P19", "status": "ARCHIVED"},
        {"phase": "P20", "status": "ARCHIVED"},
        {"phase": "P21", "status": "ARCHIVED"},
        {"phase": "P22", "status": "ARCHIVED"},
        {"phase": "P23", "status": "ARCHIVED"},
        {"phase": "P24", "status": "ARCHIVED"},
    ]
    return {
        "ok": handoff["ok"],
        "type": "paper_release_final_archive_packet",
        "phase": "P25-D1-D9",
        "release_tag": handoff["release_tag"],
        "source_handoff_status": handoff["handoff_status"],
        "archive_items": archive_items,
        "archive_item_count": len(archive_items),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def summarize_paper_release_final_archive() -> dict[str, Any]:
    archive = build_paper_release_final_archive_packet()
    archived = [item for item in archive["archive_items"] if item["status"] == "ARCHIVED"]
    return {
        "ok": len(archived) == archive["archive_item_count"],
        "type": "paper_release_final_archive_summary",
        "release_tag": archive["release_tag"],
        "archive_item_count": archive["archive_item_count"],
        "archived_count": len(archived),
        "latest_phase": archive["archive_items"][-1]["phase"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def evaluate_paper_release_final_archive_safety() -> dict[str, Any]:
    archive = build_paper_release_final_archive_packet()
    summary = summarize_paper_release_final_archive()
    passed = (
        archive["ok"] is True
        and summary["ok"] is True
        and archive["source_handoff_status"] == "READY_FOR_INDEX_ARCHIVE"
        and archive["paper_only"] is True
        and archive["local_only"] is True
        and archive["read_only"] is True
        and archive["deploy_enabled"] is False
        and archive["real_trading_enabled"] is False
        and archive["operator_review_required"] is True
    )
    return {
        "ok": passed,
        "type": "paper_release_final_archive_safety_gate",
        "status": "PASSED" if passed else "FAILED",
        "archive_item_count": archive["archive_item_count"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "real_money_impact": False,
        "operator_review_required": True,
    }


def build_paper_release_final_archive_readable_report() -> dict[str, Any]:
    summary = summarize_paper_release_final_archive()
    return {
        "ok": summary["ok"],
        "type": "paper_release_final_archive_readable_report",
        "title": "P25 Paper Release Final Archive Readable Report",
        "release_tag": summary["release_tag"],
        "archive_item_count": summary["archive_item_count"],
        "archived_count": summary["archived_count"],
        "latest_phase": summary["latest_phase"],
        "safety_summary": "paper-only, local-only, read-only, no deploy, no real trading",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def build_paper_release_final_archive_operator_checklist() -> dict[str, Any]:
    checklist = [
        {"item": "P14 final archive reviewed", "required": True, "status": "READY"},
        {"item": "P15 final archive reviewed", "required": True, "status": "READY"},
        {"item": "P16 final archive reviewed", "required": True, "status": "READY"},
        {"item": "P17 final archive reviewed", "required": True, "status": "READY"},
        {"item": "P18 final archive reviewed", "required": True, "status": "READY"},
        {"item": "P19 final archive reviewed", "required": True, "status": "READY"},
        {"item": "P20 final archive reviewed", "required": True, "status": "READY"},
        {"item": "P21 final archive reviewed", "required": True, "status": "READY"},
        {"item": "P22 final archive reviewed", "required": True, "status": "READY"},
        {"item": "P23 final archive reviewed", "required": True, "status": "READY"},
        {"item": "P24 final archive reviewed", "required": True, "status": "READY"},
        {"item": "no deploy confirmed", "required": True, "status": "READY"},
        {"item": "no real trading confirmed", "required": True, "status": "READY"},
    ]
    return {
        "ok": True,
        "type": "paper_release_final_archive_operator_checklist",
        "check_count": len(checklist),
        "checklist": checklist,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def evaluate_paper_release_final_archive_completion_gate() -> dict[str, Any]:
    report = build_paper_release_final_archive_readable_report()
    checklist = build_paper_release_final_archive_operator_checklist()
    safety = evaluate_paper_release_final_archive_safety()
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
        "type": "paper_release_final_archive_completion_gate",
        "status": "PASSED" if passed else "FAILED",
        "all_required_checks_ready": all_ready,
        "archive_item_count": report["archive_item_count"],
        "check_count": checklist["check_count"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def build_paper_release_final_archive_export_packet() -> dict[str, Any]:
    archive = build_paper_release_final_archive_packet()
    readable = build_paper_release_final_archive_readable_report()
    checklist = build_paper_release_final_archive_operator_checklist()
    completion = evaluate_paper_release_final_archive_completion_gate()
    safety = evaluate_paper_release_final_archive_safety()
    return {
        "ok": archive["ok"] and readable["ok"] and checklist["ok"] and completion["ok"] and safety["ok"],
        "type": "paper_release_final_archive_export_packet",
        "phase": "P25-D7-D9",
        "release_tag": archive["release_tag"],
        "archive": archive,
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


def build_paper_release_final_archive_closeout_checkpoint() -> dict[str, Any]:
    packet = build_paper_release_final_archive_export_packet()
    return {
        "ok": packet["ok"],
        "type": "paper_release_final_archive_closeout_checkpoint",
        "phase": "P25-D7-D9",
        "release_tag": packet["release_tag"],
        "completed": [
            "final_archive_packet",
            "final_archive_summary",
            "final_archive_safety_gate",
            "final_archive_readable_report",
            "final_archive_operator_checklist",
            "final_archive_completion_gate",
            "final_archive_export_packet",
            "final_archive_closeout_checkpoint",
            "final_archive_handoff_packet",
        ],
        "completion_gate_status": packet["completion_gate"]["status"],
        "safety_gate_status": packet["safety_gate"]["status"],
        "archive_item_count": packet["archive"]["archive_item_count"],
        "check_count": packet["operator_checklist"]["check_count"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def build_paper_release_final_archive_handoff_packet() -> dict[str, Any]:
    closeout = build_paper_release_final_archive_closeout_checkpoint()
    return {
        "ok": closeout["ok"],
        "type": "paper_release_final_archive_handoff_packet",
        "release_tag": closeout["release_tag"],
        "phase": "P25-D7-D9",
        "handoff_status": "READY_FOR_FINAL_ARCHIVE_CLOSEOUT" if closeout["ok"] else "BLOCKED",
        "closeout": closeout,
        "next_phase_candidate": "P25 Final Closeout Acceptance",
        "safety_boundary": "paper-only, local-only, read-only, no deploy, no real trading",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }
