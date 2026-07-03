from __future__ import annotations

from typing import Any

from btc_finance_platform.operator_evidence_archive_view import build_operator_evidence_archive_closeout_checkpoint
from btc_finance_platform.operator_evidence_archive_view import build_operator_evidence_archive_export_packet


def build_local_evidence_final_review_packet() -> dict[str, Any]:
    archive_packet = build_operator_evidence_archive_export_packet()
    archive_closeout = build_operator_evidence_archive_closeout_checkpoint()

    return {
        "ok": archive_packet["ok"] and archive_closeout["ok"],
        "type": "local_evidence_final_review_packet",
        "phase": "P20-D1-D3",
        "release_tag": "v14-learning-engine-paper",
        "review_scope": [
            "P14 paper release evidence",
            "P15 post release continuity",
            "P16 operator evidence console",
            "P17 local evidence export files",
            "P18 local evidence navigation",
            "P19 local evidence archive view",
        ],
        "archive_packet_status": "PASSED" if archive_packet["ok"] else "FAILED",
        "archive_closeout_status": "PASSED" if archive_closeout["ok"] else "FAILED",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def evaluate_local_evidence_final_review_safety() -> dict[str, Any]:
    packet = build_local_evidence_final_review_packet()
    passed = (
        packet["ok"] is True
        and packet["paper_only"] is True
        and packet["local_only"] is True
        and packet["read_only"] is True
        and packet["deploy_enabled"] is False
        and packet["real_trading_enabled"] is False
        and packet["operator_review_required"] is True
    )

    return {
        "ok": passed,
        "type": "local_evidence_final_review_safety_gate",
        "status": "PASSED" if passed else "FAILED",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
        "real_money_impact": False,
    }


def build_local_evidence_final_review_summary() -> dict[str, Any]:
    packet = build_local_evidence_final_review_packet()
    safety = evaluate_local_evidence_final_review_safety()

    return {
        "ok": packet["ok"] and safety["ok"],
        "type": "local_evidence_final_review_summary",
        "title": "P20 Local Evidence Console Final Review",
        "release_tag": packet["release_tag"],
        "review_item_count": len(packet["review_scope"]),
        "safety_gate_status": safety["status"],
        "summary": "Final read-only review packet for local evidence console chain.",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }
