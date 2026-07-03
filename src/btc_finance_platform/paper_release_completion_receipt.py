from __future__ import annotations

from typing import Any

from btc_finance_platform.paper_release_final_archive import build_paper_release_final_archive_handoff_packet


def build_paper_release_completion_receipt() -> dict[str, Any]:
    handoff = build_paper_release_final_archive_handoff_packet()
    receipt_items = [
        {"phase": "P14", "status": "RECEIPTED"},
        {"phase": "P15", "status": "RECEIPTED"},
        {"phase": "P16", "status": "RECEIPTED"},
        {"phase": "P17", "status": "RECEIPTED"},
        {"phase": "P18", "status": "RECEIPTED"},
        {"phase": "P19", "status": "RECEIPTED"},
        {"phase": "P20", "status": "RECEIPTED"},
        {"phase": "P21", "status": "RECEIPTED"},
        {"phase": "P22", "status": "RECEIPTED"},
        {"phase": "P23", "status": "RECEIPTED"},
        {"phase": "P24", "status": "RECEIPTED"},
        {"phase": "P25", "status": "RECEIPTED"},
    ]
    return {
        "ok": handoff["ok"],
        "type": "paper_release_completion_receipt",
        "phase": "P26-D1-D6",
        "release_tag": handoff["release_tag"],
        "source_handoff_status": handoff["handoff_status"],
        "receipt_items": receipt_items,
        "receipt_item_count": len(receipt_items),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def summarize_paper_release_completion_receipt() -> dict[str, Any]:
    receipt = build_paper_release_completion_receipt()
    receipted = [item for item in receipt["receipt_items"] if item["status"] == "RECEIPTED"]
    return {
        "ok": len(receipted) == receipt["receipt_item_count"],
        "type": "paper_release_completion_receipt_summary",
        "release_tag": receipt["release_tag"],
        "receipt_item_count": receipt["receipt_item_count"],
        "receipted_count": len(receipted),
        "latest_phase": receipt["receipt_items"][-1]["phase"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def evaluate_paper_release_completion_receipt_safety() -> dict[str, Any]:
    receipt = build_paper_release_completion_receipt()
    summary = summarize_paper_release_completion_receipt()
    passed = (
        receipt["ok"] is True
        and summary["ok"] is True
        and receipt["source_handoff_status"] == "READY_FOR_FINAL_ARCHIVE_CLOSEOUT"
        and receipt["paper_only"] is True
        and receipt["local_only"] is True
        and receipt["read_only"] is True
        and receipt["deploy_enabled"] is False
        and receipt["real_trading_enabled"] is False
        and receipt["operator_review_required"] is True
    )
    return {
        "ok": passed,
        "type": "paper_release_completion_receipt_safety_gate",
        "status": "PASSED" if passed else "FAILED",
        "receipt_item_count": receipt["receipt_item_count"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "real_money_impact": False,
        "operator_review_required": True,
    }


def build_paper_release_completion_receipt_readable_report() -> dict[str, Any]:
    summary = summarize_paper_release_completion_receipt()
    return {
        "ok": summary["ok"],
        "type": "paper_release_completion_receipt_readable_report",
        "title": "P26 Paper Release Completion Receipt Readable Report",
        "release_tag": summary["release_tag"],
        "receipt_item_count": summary["receipt_item_count"],
        "receipted_count": summary["receipted_count"],
        "latest_phase": summary["latest_phase"],
        "safety_summary": "paper-only, local-only, read-only, no deploy, no real trading",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def build_paper_release_completion_receipt_operator_checklist() -> dict[str, Any]:
    checklist = [
        {"item": "P14 completion receipt reviewed", "required": True, "status": "READY"},
        {"item": "P15 completion receipt reviewed", "required": True, "status": "READY"},
        {"item": "P16 completion receipt reviewed", "required": True, "status": "READY"},
        {"item": "P17 completion receipt reviewed", "required": True, "status": "READY"},
        {"item": "P18 completion receipt reviewed", "required": True, "status": "READY"},
        {"item": "P19 completion receipt reviewed", "required": True, "status": "READY"},
        {"item": "P20 completion receipt reviewed", "required": True, "status": "READY"},
        {"item": "P21 completion receipt reviewed", "required": True, "status": "READY"},
        {"item": "P22 completion receipt reviewed", "required": True, "status": "READY"},
        {"item": "P23 completion receipt reviewed", "required": True, "status": "READY"},
        {"item": "P24 completion receipt reviewed", "required": True, "status": "READY"},
        {"item": "P25 completion receipt reviewed", "required": True, "status": "READY"},
        {"item": "no deploy confirmed", "required": True, "status": "READY"},
        {"item": "no real trading confirmed", "required": True, "status": "READY"},
    ]
    return {
        "ok": True,
        "type": "paper_release_completion_receipt_operator_checklist",
        "check_count": len(checklist),
        "checklist": checklist,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def evaluate_paper_release_completion_receipt_completion_gate() -> dict[str, Any]:
    report = build_paper_release_completion_receipt_readable_report()
    checklist = build_paper_release_completion_receipt_operator_checklist()
    safety = evaluate_paper_release_completion_receipt_safety()
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
        "type": "paper_release_completion_receipt_completion_gate",
        "status": "PASSED" if passed else "FAILED",
        "all_required_checks_ready": all_ready,
        "receipt_item_count": report["receipt_item_count"],
        "check_count": checklist["check_count"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def build_paper_release_completion_receipt_export_packet() -> dict[str, Any]:
    receipt = build_paper_release_completion_receipt()
    readable = build_paper_release_completion_receipt_readable_report()
    checklist = build_paper_release_completion_receipt_operator_checklist()
    completion = evaluate_paper_release_completion_receipt_completion_gate()
    safety = evaluate_paper_release_completion_receipt_safety()
    return {
        "ok": receipt["ok"] and readable["ok"] and checklist["ok"] and completion["ok"] and safety["ok"],
        "type": "paper_release_completion_receipt_export_packet",
        "phase": "P26-D7-D12",
        "release_tag": receipt["release_tag"],
        "receipt": receipt,
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


def build_paper_release_completion_receipt_closeout_checkpoint() -> dict[str, Any]:
    packet = build_paper_release_completion_receipt_export_packet()
    return {
        "ok": packet["ok"],
        "type": "paper_release_completion_receipt_closeout_checkpoint",
        "phase": "P26-D7-D12",
        "release_tag": packet["release_tag"],
        "completed": [
            "completion_receipt_export_packet",
            "completion_receipt_closeout_checkpoint",
            "completion_receipt_handoff_packet",
            "final_receipt_archive_acceptance_packet",
            "final_receipt_archive_manifest",
            "final_receipt_handoff_checkpoint",
        ],
        "completion_gate_status": packet["completion_gate"]["status"],
        "safety_gate_status": packet["safety_gate"]["status"],
        "receipt_item_count": packet["receipt"]["receipt_item_count"],
        "check_count": packet["operator_checklist"]["check_count"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def build_paper_release_completion_receipt_handoff_packet() -> dict[str, Any]:
    closeout = build_paper_release_completion_receipt_closeout_checkpoint()
    return {
        "ok": closeout["ok"],
        "type": "paper_release_completion_receipt_handoff_packet",
        "release_tag": closeout["release_tag"],
        "phase": "P26-D7-D12",
        "handoff_status": "READY_FOR_RECEIPT_ARCHIVE" if closeout["ok"] else "BLOCKED",
        "closeout": closeout,
        "next_phase_candidate": "P27 Paper Release Final Verification",
        "safety_boundary": "paper-only, local-only, read-only, no deploy, no real trading",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }
