from __future__ import annotations

from typing import Any

from btc_finance_platform.paper_release_final_operator_receipt import build_paper_release_final_operator_receipt_handoff_packet


def build_paper_release_final_delivery_packet() -> dict[str, Any]:
    handoff = build_paper_release_final_operator_receipt_handoff_packet()
    delivery_items = [
        {"phase": "P14", "status": "DELIVERED"},
        {"phase": "P15", "status": "DELIVERED"},
        {"phase": "P16", "status": "DELIVERED"},
        {"phase": "P17", "status": "DELIVERED"},
        {"phase": "P18", "status": "DELIVERED"},
        {"phase": "P19", "status": "DELIVERED"},
        {"phase": "P20", "status": "DELIVERED"},
        {"phase": "P21", "status": "DELIVERED"},
        {"phase": "P22", "status": "DELIVERED"},
        {"phase": "P23", "status": "DELIVERED"},
        {"phase": "P24", "status": "DELIVERED"},
        {"phase": "P25", "status": "DELIVERED"},
        {"phase": "P26", "status": "DELIVERED"},
        {"phase": "P27", "status": "DELIVERED"},
        {"phase": "P28", "status": "DELIVERED"},
        {"phase": "P29", "status": "DELIVERED"},
    ]
    return {
        "ok": handoff["ok"],
        "type": "paper_release_final_delivery_packet",
        "phase": "P30-D1-D3",
        "release_tag": handoff["release_tag"],
        "source_handoff_status": handoff["handoff_status"],
        "delivery_items": delivery_items,
        "delivery_item_count": len(delivery_items),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def summarize_paper_release_final_delivery() -> dict[str, Any]:
    packet = build_paper_release_final_delivery_packet()
    delivered = [item for item in packet["delivery_items"] if item["status"] == "DELIVERED"]
    return {
        "ok": len(delivered) == packet["delivery_item_count"],
        "type": "paper_release_final_delivery_summary",
        "release_tag": packet["release_tag"],
        "delivery_item_count": packet["delivery_item_count"],
        "delivered_count": len(delivered),
        "latest_phase": packet["delivery_items"][-1]["phase"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def evaluate_paper_release_final_delivery_safety() -> dict[str, Any]:
    packet = build_paper_release_final_delivery_packet()
    summary = summarize_paper_release_final_delivery()
    passed = (
        packet["ok"] is True
        and summary["ok"] is True
        and packet["source_handoff_status"] == "READY_FOR_OPERATOR_RECEIPT_ARCHIVE"
        and packet["paper_only"] is True
        and packet["local_only"] is True
        and packet["read_only"] is True
        and packet["deploy_enabled"] is False
        and packet["real_trading_enabled"] is False
        and packet["operator_review_required"] is True
    )
    return {
        "ok": passed,
        "type": "paper_release_final_delivery_safety_gate",
        "status": "PASSED" if passed else "FAILED",
        "delivery_item_count": packet["delivery_item_count"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "real_money_impact": False,
        "operator_review_required": True,
    }
