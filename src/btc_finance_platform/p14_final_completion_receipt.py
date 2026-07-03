import json
from pathlib import Path
from typing import Any


REQUIRED_COMPLETION_ITEMS = (
    "p14_learning_engine_closeout",
    "p14_final_archive_manifest",
    "p14_final_operator_acceptance_packet",
    "p14_final_branch_handoff_checkpoint",
    "p14_human_merge_plan",
    "p14_human_release_plan",
    "all_checks_passed",
    "pytest_passed",
    "repo_clean",
)


def normalize_completion_item(item: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise ValueError("completion item must be a dict")

    item_key = item.get("item_key")
    if not item_key:
        raise ValueError("item_key is required")

    return {
        "item_key": str(item_key),
        "status": str(item.get("status", "complete")),
        "human_operator_required": bool(item.get("human_operator_required", True)),
        "auto_execute_allowed": bool(item.get("auto_execute_allowed", False)),
        "auto_merge_allowed": bool(item.get("auto_merge_allowed", False)),
        "auto_tag_allowed": bool(item.get("auto_tag_allowed", False)),
        "auto_release_allowed": bool(item.get("auto_release_allowed", False)),
        "auto_deploy_allowed": bool(item.get("auto_deploy_allowed", False)),
        "real_world_actions_allowed": bool(item.get("real_world_actions_allowed", False)),
    }


def default_final_completion_items() -> list[dict[str, Any]]:
    return [
        {"item_key": "p14_learning_engine_closeout", "status": "complete"},
        {"item_key": "p14_final_archive_manifest", "status": "complete"},
        {"item_key": "p14_final_operator_acceptance_packet", "status": "complete"},
        {"item_key": "p14_final_branch_handoff_checkpoint", "status": "complete"},
        {"item_key": "p14_human_merge_plan", "status": "complete"},
        {"item_key": "p14_human_release_plan", "status": "complete"},
        {"item_key": "all_checks_passed", "status": "complete"},
        {"item_key": "pytest_passed", "status": "complete"},
        {"item_key": "repo_clean", "status": "complete"},
    ]


def build_final_completion_receipt(
    branch_name: str,
    validation_passed_count: int,
    completion_items: list[dict[str, Any]],
) -> dict[str, Any]:
    if not branch_name:
        raise ValueError("branch_name is required")

    if not isinstance(validation_passed_count, int) or validation_passed_count <= 0:
        raise ValueError("validation_passed_count must be a positive integer")

    if not isinstance(completion_items, list):
        raise ValueError("completion_items must be a list")

    rows = [normalize_completion_item(item) for item in completion_items]
    present = {row["item_key"] for row in rows}
    missing_items = [key for key in REQUIRED_COMPLETION_ITEMS if key not in present]

    unsafe_rows = [
        row for row in rows
        if row["human_operator_required"] is not True
        or row["auto_execute_allowed"] is not False
        or row["auto_merge_allowed"] is not False
        or row["auto_tag_allowed"] is not False
        or row["auto_release_allowed"] is not False
        or row["auto_deploy_allowed"] is not False
        or row["real_world_actions_allowed"] is not False
    ]

    non_complete_rows = [row for row in rows if row["status"] != "complete"]

    if missing_items:
        completion_status = "BLOCKED_MISSING_COMPLETION_ITEM"
    elif unsafe_rows:
        completion_status = "BLOCKED_SAFETY_BOUNDARY_VIOLATION"
    elif non_complete_rows:
        completion_status = "BLOCKED_NON_COMPLETE_ITEM"
    else:
        completion_status = "P14_COMPLETE_READY_FOR_HUMAN_CONTROLLED_NEXT_STEP"

    return {
        "ok": True,
        "type": "p14_final_completion_receipt",
        "current_stage": "P14-D61-D63",
        "branch_name": branch_name,
        "validation_passed_count": validation_passed_count,
        "completion_status": completion_status,
        "purpose": "final P14 completion receipt without executing merge, tag, release, or deploy",
        "required_completion_items": list(REQUIRED_COMPLETION_ITEMS),
        "missing_items": missing_items,
        "unsafe_item_count": len(unsafe_rows),
        "unsafe_items": unsafe_rows,
        "non_complete_item_count": len(non_complete_rows),
        "non_complete_items": non_complete_rows,
        "rows": rows,
        "completion_policy": {
            "p14_complete_after_operator_review": completion_status == "P14_COMPLETE_READY_FOR_HUMAN_CONTROLLED_NEXT_STEP",
            "merge_to_main_allowed_now": False,
            "tag_allowed_now": False,
            "release_allowed_now": False,
            "deploy_allowed_now": False,
            "auto_execute_allowed": False,
            "auto_merge_allowed": False,
            "auto_tag_allowed": False,
            "auto_release_allowed": False,
            "auto_deploy_allowed": False,
            "human_operator_required": True,
            "operator_review_required": True,
        },
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
    }


def write_final_completion_receipt(
    branch_name: str,
    validation_passed_count: int,
    completion_items: list[dict[str, Any]],
    path: str | Path,
) -> dict[str, Any]:
    receipt = build_final_completion_receipt(
        branch_name=branch_name,
        validation_passed_count=validation_passed_count,
        completion_items=completion_items,
    )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p14_final_completion_receipt_written",
        "output_path": str(output),
        "receipt": receipt,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "auto_execute_allowed": False,
        "auto_merge_allowed": False,
        "auto_tag_allowed": False,
        "auto_release_allowed": False,
        "auto_deploy_allowed": False,
        "real_world_actions_allowed": False,
    }
