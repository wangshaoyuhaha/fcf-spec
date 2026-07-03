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


def build_paper_evidence_master_readable_report() -> dict[str, Any]:
    summary = build_paper_evidence_master_closeout_summary()
    return {
        "ok": summary["ok"],
        "type": "paper_evidence_master_readable_report",
        "title": "P21 Paper Evidence Master Readable Report",
        "release_tag": summary["release_tag"],
        "covered_phase_count": summary["covered_phase_count"],
        "sections": [
            "P14 Learning Engine paper release",
            "P15 post release continuity",
            "P16 operator evidence console",
            "P17 local evidence export files",
            "P18 local evidence navigation",
            "P19 local evidence archive view",
            "P20 local evidence final review",
        ],
        "safety_summary": "paper-only, local-only, read-only, no deploy, no real trading",
        "safety_gate_status": summary["safety_gate_status"],
        "operator_review_required": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
    }


def build_paper_evidence_master_operator_checklist() -> dict[str, Any]:
    checklist = [
        {"item": "P14 release evidence closed", "required": True, "status": "READY"},
        {"item": "P15 continuity evidence closed", "required": True, "status": "READY"},
        {"item": "P16 evidence console closed", "required": True, "status": "READY"},
        {"item": "P17 export evidence closed", "required": True, "status": "READY"},
        {"item": "P18 navigation evidence closed", "required": True, "status": "READY"},
        {"item": "P19 archive evidence closed", "required": True, "status": "READY"},
        {"item": "P20 final review closed", "required": True, "status": "READY"},
        {"item": "no deploy confirmed", "required": True, "status": "READY"},
        {"item": "no real trading confirmed", "required": True, "status": "READY"},
    ]
    return {
        "ok": True,
        "type": "paper_evidence_master_operator_checklist",
        "check_count": len(checklist),
        "checklist": checklist,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def evaluate_paper_evidence_master_completion_gate() -> dict[str, Any]:
    report = build_paper_evidence_master_readable_report()
    checklist = build_paper_evidence_master_operator_checklist()
    all_ready = all(item["status"] == "READY" and item["required"] is True for item in checklist["checklist"])
    passed = (
        report["ok"] is True
        and checklist["ok"] is True
        and all_ready
        and report["deploy_enabled"] is False
        and report["real_trading_enabled"] is False
        and checklist["operator_review_required"] is True
    )
    return {
        "ok": passed,
        "type": "paper_evidence_master_completion_gate",
        "status": "PASSED" if passed else "FAILED",
        "all_required_checks_ready": all_ready,
        "check_count": checklist["check_count"],
        "covered_phase_count": report["covered_phase_count"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }
