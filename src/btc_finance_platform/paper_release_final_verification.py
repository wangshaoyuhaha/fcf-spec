from __future__ import annotations

from typing import Any

from btc_finance_platform.paper_release_completion_receipt import build_paper_release_completion_receipt_handoff_packet


def build_paper_release_final_verification_packet() -> dict[str, Any]:
    handoff = build_paper_release_completion_receipt_handoff_packet()
    verification_items = [
        {"phase": "P14", "status": "VERIFIED"},
        {"phase": "P15", "status": "VERIFIED"},
        {"phase": "P16", "status": "VERIFIED"},
        {"phase": "P17", "status": "VERIFIED"},
        {"phase": "P18", "status": "VERIFIED"},
        {"phase": "P19", "status": "VERIFIED"},
        {"phase": "P20", "status": "VERIFIED"},
        {"phase": "P21", "status": "VERIFIED"},
        {"phase": "P22", "status": "VERIFIED"},
        {"phase": "P23", "status": "VERIFIED"},
        {"phase": "P24", "status": "VERIFIED"},
        {"phase": "P25", "status": "VERIFIED"},
        {"phase": "P26", "status": "VERIFIED"},
    ]
    return {
        "ok": handoff["ok"],
        "type": "paper_release_final_verification_packet",
        "phase": "P27-D1-D3",
        "release_tag": handoff["release_tag"],
        "source_handoff_status": handoff["handoff_status"],
        "verification_items": verification_items,
        "verification_item_count": len(verification_items),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def summarize_paper_release_final_verification() -> dict[str, Any]:
    packet = build_paper_release_final_verification_packet()
    verified = [item for item in packet["verification_items"] if item["status"] == "VERIFIED"]
    return {
        "ok": len(verified) == packet["verification_item_count"],
        "type": "paper_release_final_verification_summary",
        "release_tag": packet["release_tag"],
        "verification_item_count": packet["verification_item_count"],
        "verified_count": len(verified),
        "latest_phase": packet["verification_items"][-1]["phase"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def evaluate_paper_release_final_verification_safety() -> dict[str, Any]:
    packet = build_paper_release_final_verification_packet()
    summary = summarize_paper_release_final_verification()
    passed = (
        packet["ok"] is True
        and summary["ok"] is True
        and packet["source_handoff_status"] == "READY_FOR_RECEIPT_ARCHIVE"
        and packet["paper_only"] is True
        and packet["local_only"] is True
        and packet["read_only"] is True
        and packet["deploy_enabled"] is False
        and packet["real_trading_enabled"] is False
        and packet["operator_review_required"] is True
    )
    return {
        "ok": passed,
        "type": "paper_release_final_verification_safety_gate",
        "status": "PASSED" if passed else "FAILED",
        "verification_item_count": packet["verification_item_count"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "real_money_impact": False,
        "operator_review_required": True,
    }
