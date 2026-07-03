import json
from pathlib import Path
from typing import Any

from btc_finance_platform.p13_ai_learning_audit_report import build_ai_learning_audit_report
from btc_finance_platform.p13_branch_closeout import build_p13_branch_closeout_manifest


def build_p13_final_closeout_summary(
    output_path: str | Path,
    ledger_path: str | Path,
) -> dict[str, Any]:
    branch_manifest = build_p13_branch_closeout_manifest(output_path)
    audit_report = build_ai_learning_audit_report(ledger_path)

    if branch_manifest.get("p13_scope_closed") is not True:
        raise ValueError("P13 branch scope must be closed")

    if audit_report.get("audit_status") != "READY_FOR_OPERATOR_REVIEW":
        raise ValueError("AI learning audit must be ready for operator review")

    return {
        "ok": True,
        "type": "p13_final_closeout_summary",
        "current_stage": "P13-D28-D30",
        "p13_final_status": "READY_FOR_MANUAL_MAIN_MERGE_REVIEW",
        "p13_completed": True,
        "merge_to_main_completed": False,
        "release_created": False,
        "operator_console_completed": True,
        "ai_learning_boundary_completed": True,
        "ai_learning_memory_ledger_completed": True,
        "ai_learning_audit_report_completed": True,
        "paper_only": True,
        "local_only": True,
        "ui_mode": "read_only",
        "operator_review_required": True,
        "trading_buttons_enabled": False,
        "real_exchange_api": False,
        "real_brokerage_api": False,
        "real_api_key_required": False,
        "wallet_private_key_required": False,
        "real_order": False,
        "real_execution": False,
        "real_balance": False,
        "real_position": False,
        "real_money_impact": False,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "patch_auto_apply_allowed": False,
        "auto_merge_allowed": False,
        "auto_release_allowed": False,
        "completed_units": [
            "P13-D1-D3 read-only operator console skeleton",
            "P13-D4-D6 operator console launcher",
            "P13-D7-D9 operator console status snapshot",
            "P13-D10-D12 operator review packet",
            "P13-D13-D15 operator console acceptance summary",
            "P13-D16-D18 branch closeout manifest",
            "P13-D19-D21 AI learning self-audit boundary",
            "P13-D22-D24 AI learning memory ledger",
            "P13-D25-D27 AI learning audit report",
            "P13-D28-D30 final closeout summary",
        ],
        "manual_next_step": "run final branch sync check before any main merge",
        "branch_manifest": branch_manifest,
        "ai_learning_audit_report": audit_report,
    }


def write_p13_final_closeout_summary(
    output_path: str | Path,
    ledger_path: str | Path,
    summary_path: str | Path,
) -> dict[str, Any]:
    summary = build_p13_final_closeout_summary(output_path, ledger_path)
    path = Path(summary_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p13_final_closeout_summary_written",
        "summary_path": str(path),
        "summary": summary,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "merge_to_main_completed": False,
        "release_created": False,
    }
