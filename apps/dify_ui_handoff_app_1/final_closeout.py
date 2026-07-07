"""DIFY-UI-HANDOFF-D6 final closeout."""

from __future__ import annotations

from typing import Any, Dict, List

from apps.dify_ui_handoff_app_1.contract import APP_ID
from apps.dify_ui_handoff_app_1.manual_workflow_guide import summarize_dify_manual_workflow_guide
from apps.dify_ui_handoff_app_1.prompt_template import summarize_dify_prompt_package

STAGE_ID = "DIFY-UI-HANDOFF-D6"
SIDECAR_BRANCH = "sidecar-dify-ui-handoff-app-1"

COMPLETED_STAGES: List[str] = [
    "DIFY-UI-HANDOFF-D1",
    "DIFY-UI-HANDOFF-D2",
    "DIFY-UI-HANDOFF-D3",
    "DIFY-UI-HANDOFF-D4",
    "DIFY-UI-HANDOFF-D5",
    "DIFY-UI-HANDOFF-D6",
]

SAFETY: Dict[str, Any] = {
    "paper_only": True,
    "local_only": True,
    "read_only": True,
    "sidecar_only": True,
    "operator_review_required": True,
    "manual_configuration_only": True,
    "no_core_mutation": True,
    "no_p48": True,
    "no_deploy": True,
    "no_release": True,
    "no_dify_api_write": True,
    "no_auto_dify_app_creation": True,
    "no_broker_connection": True,
    "no_exchange_connection": True,
    "no_credential_request": True,
    "no_wallet_private_key_request": True,
    "no_real_account_access": True,
    "no_real_balance_read": True,
    "no_real_position_read": True,
    "no_real_order": True,
    "no_real_execution": True,
    "no_real_money_impact": True,
    "no_operator_review_bypass": True,
    "real_execution_allowed": False,
    "trade_action_enabled": False,
    "dify_api_write_allowed": False,
    "automated_dify_app_creation_allowed": False,
    "auto_merge_allowed": False,
}

def build_final_closeout() -> Dict[str, Any]:
    prompt_summary = summarize_dify_prompt_package()
    guide_summary = summarize_dify_manual_workflow_guide()
    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "sidecar_branch": SIDECAR_BRANCH,
        "status": "completed",
        "completed_stages": list(COMPLETED_STAGES),
        "prompt_summary": prompt_summary,
        "manual_workflow_guide_summary": guide_summary,
        "safety": dict(SAFETY),
        "ready_for_operator_merge_review": True,
        "auto_merge_allowed": False,
        "release_allowed": False,
        "deploy_allowed": False,
        "next_operator_step": "return_to_main_architecture_window_for_merge_review",
    }

def validate_final_closeout() -> Dict[str, Any]:
    closeout = build_final_closeout()
    issues = []
    if closeout["app_id"] != APP_ID:
        issues.append("app_id mismatch")
    if closeout["stage_id"] != STAGE_ID:
        issues.append("stage_id mismatch")
    if closeout["status"] != "completed":
        issues.append("status mismatch")
    if len(closeout["completed_stages"]) != 6:
        issues.append("completed stage count mismatch")
    if closeout["prompt_summary"]["valid"] is not True:
        issues.append("prompt summary invalid")
    if closeout["manual_workflow_guide_summary"]["valid"] is not True:
        issues.append("manual workflow guide invalid")
    for key, value in SAFETY.items():
        if closeout["safety"].get(key) is not value:
            issues.append("safety mismatch: " + key)
    if closeout["ready_for_operator_merge_review"] is not True:
        issues.append("merge review flag mismatch")
    for key in ["auto_merge_allowed", "release_allowed", "deploy_allowed"]:
        if closeout[key] is not False:
            issues.append(key + " must be false")
    return {"valid": not issues, "issues": issues, "stage_id": STAGE_ID}

def summarize_final_closeout() -> Dict[str, Any]:
    closeout = build_final_closeout()
    validation = validate_final_closeout()
    return {
        "app_id": closeout["app_id"],
        "stage_id": closeout["stage_id"],
        "status": closeout["status"],
        "valid": validation["valid"],
        "completed_stage_count": len(closeout["completed_stages"]),
        "ready_for_operator_merge_review": closeout["ready_for_operator_merge_review"],
        "auto_merge_allowed": closeout["auto_merge_allowed"],
        "release_allowed": closeout["release_allowed"],
        "deploy_allowed": closeout["deploy_allowed"],
        "paper_only": closeout["safety"]["paper_only"],
        "local_only": closeout["safety"]["local_only"],
        "read_only": closeout["safety"]["read_only"],
        "operator_review_required": closeout["safety"]["operator_review_required"],
        "real_execution_allowed": closeout["safety"]["real_execution_allowed"],
        "trade_action_enabled": closeout["safety"]["trade_action_enabled"],
        "next_operator_step": closeout["next_operator_step"],
    }
