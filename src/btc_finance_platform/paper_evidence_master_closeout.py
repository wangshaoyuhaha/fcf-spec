from __future__ import annotations

from typing import Any

from btc_finance_platform.operator_evidence_final_review import build_local_evidence_final_review_handoff_packet


def build_paper_evidence_master_closeout_packet() -> dict[str, Any]:
    handoff = build_local_evidence_final_review_handoff_packet()
    return {
        "ok": handoff["ok"],
        "type": "paper_evidence_master_closeout_packet",
        "phase": "P21-D1-D3",
        "release_tag": "v14-learning-engine-paper",
        "covered_phases": [
            "P14 Learning Engine paper release",
            "P15 post release continuity",
            "P16 operator evidence console",
            "P17 local evidence export files",
            "P18 local evidence navigation",
            "P19 local evidence archive view",
            "P20 local evidence final review",
        ],
        "handoff_status": handoff["handoff_status"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def evaluate_paper_evidence_master_closeout_safety() -> dict[str, Any]:
    packet = build_paper_evidence_master_closeout_packet()
    passed = (
        packet["ok"] is True
        and packet["paper_only"] is True
        and packet["local_only"] is True
        and packet["read_only"] is True
        and packet["deploy_enabled"] is False
        and packet["real_trading_enabled"] is False
        and packet["operator_review_required"] is True
        and packet["handoff_status"] == "READY_FOR_FINAL_ARCHIVE"
    )
    return {
        "ok": passed,
        "type": "paper_evidence_master_closeout_safety_gate",
        "status": "PASSED" if passed else "FAILED",
        "covered_phase_count": len(packet["covered_phases"]),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "real_money_impact": False,
        "operator_review_required": True,
    }


def build_paper_evidence_master_closeout_summary() -> dict[str, Any]:
    packet = build_paper_evidence_master_closeout_packet()
    safety = evaluate_paper_evidence_master_closeout_safety()
    return {
        "ok": packet["ok"] and safety["ok"],
        "type": "paper_evidence_master_closeout_summary",
        "title": "P21 Paper Evidence Console Master Closeout",
        "release_tag": packet["release_tag"],
        "covered_phase_count": len(packet["covered_phases"]),
        "safety_gate_status": safety["status"],
        "summary": "Master closeout for the paper-only evidence console chain.",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }
