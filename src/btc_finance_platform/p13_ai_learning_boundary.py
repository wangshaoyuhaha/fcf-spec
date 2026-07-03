import json
from pathlib import Path
from typing import Any


def build_ai_learning_self_audit_boundary() -> dict[str, Any]:
    return {
        "ok": True,
        "type": "p13_ai_learning_self_audit_boundary",
        "current_stage": "P13-D19-D21",
        "learning_enabled": True,
        "learning_mode": "audit_and_proposal_only",
        "memory_required": True,
        "self_audit_enabled": True,
        "bug_detection_enabled": True,
        "patch_proposal_enabled": True,
        "patch_auto_apply_allowed": False,
        "auto_merge_allowed": False,
        "auto_release_allowed": False,
        "auto_deploy_allowed": False,
        "ai_may_generate_patch_proposal": True,
        "ai_may_generate_tests": True,
        "ai_may_explain_python_outputs": True,
        "ai_may_adjust_real_money": False,
        "ai_may_place_real_order": False,
        "ai_may_use_api_key": False,
        "ai_may_use_wallet_private_key": False,
        "operator_review_required": True,
        "paper_only": True,
        "local_only": True,
        "ui_mode": "read_only",
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
        "memory_layers": [
            "runtime_status_memory",
            "decision_log_memory",
            "model_card_memory",
            "validation_history_memory",
            "operator_review_memory",
        ],
        "forbidden_memory": [
            "api_keys",
            "wallet_private_keys",
            "real_exchange_credentials",
            "real_brokerage_credentials",
        ],
        "self_audit_checks": [
            "paper_only_boundary_check",
            "operator_review_required_check",
            "forbidden_real_action_flag_check",
            "pytest_regression_check",
            "run_all_checks_gate",
            "patch_proposal_requires_review",
        ],
        "safe_learning_loop": [
            "observe_result",
            "record_decision_outcome",
            "detect_possible_issue",
            "generate_review_note",
            "generate_patch_proposal",
            "generate_tests",
            "wait_for_operator_review",
        ],
    }


def write_ai_learning_self_audit_boundary(path: str | Path) -> dict[str, Any]:
    boundary = build_ai_learning_self_audit_boundary()
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(boundary, indent=2, sort_keys=True), encoding="utf-8")
    return {
        "ok": True,
        "type": "p13_ai_learning_self_audit_boundary_written",
        "output_path": str(output),
        "boundary": boundary,
        "paper_only": True,
        "local_only": True,
        "ui_mode": "read_only",
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "patch_auto_apply_allowed": False,
    }
