import json
from pathlib import Path
from typing import Any


REQUIRED_HANDOFF_ITEMS = (
    "p14_final_archive_manifest",
    "p14_final_operator_acceptance_packet",
    "p14_merge_readiness_bridge",
    "p14_learning_engine_closeout",
    "repo_clean",
    "all_checks_passed",
    "pytest_passed",
)


def normalize_handoff_item(item: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise ValueError("handoff item must be a dict")

    item_key = item.get("item_key")
    if not item_key:
        raise ValueError("item_key is required")

    return {
        "item_key": str(item_key),
        "status": str(item.get("status", "ready")),
        "operator_review_required": bool(item.get("operator_review_required", True)),
        "merge_auto_execute_allowed": bool(item.get("merge_auto_execute_allowed", False)),
        "release_auto_publish_allowed": bool(item.get("release_auto_publish_allowed", False)),
        "handoff_auto_apply_allowed": bool(item.get("handoff_auto_apply_allowed", False)),
        "real_world_actions_allowed": bool(item.get("real_world_actions_allowed", False)),
    }


def default_final_branch_handoff_items() -> list[dict[str, Any]]:
    return [
        {"item_key": "p14_final_archive_manifest", "status": "ready"},
        {"item_key": "p14_final_operator_acceptance_packet", "status": "ready"},
        {"item_key": "p14_merge_readiness_bridge", "status": "ready"},
        {"item_key": "p14_learning_engine_closeout", "status": "ready"},
        {"item_key": "repo_clean", "status": "ready"},
        {"item_key": "all_checks_passed", "status": "ready"},
        {"item_key": "pytest_passed", "status": "ready"},
    ]


def build_final_branch_handoff_checkpoint(
    branch_name: str,
    target_branch: str,
    latest_commit_label: str,
    validation_passed_count: int,
    handoff_items: list[dict[str, Any]],
) -> dict[str, Any]:
    if not branch_name:
        raise ValueError("branch_name is required")

    if not target_branch:
        raise ValueError("target_branch is required")

    if branch_name == target_branch:
        raise ValueError("branch_name and target_branch must differ")

    if not latest_commit_label:
        raise ValueError("latest_commit_label is required")

    if not isinstance(validation_passed_count, int) or validation_passed_count <= 0:
        raise ValueError("validation_passed_count must be a positive integer")

    if not isinstance(handoff_items, list):
        raise ValueError("handoff_items must be a list")

    rows = [normalize_handoff_item(item) for item in handoff_items]
    present = {row["item_key"] for row in rows}
    missing_items = [key for key in REQUIRED_HANDOFF_ITEMS if key not in present]

    unsafe_rows = [
        row for row in rows
        if row["operator_review_required"] is not True
        or row["merge_auto_execute_allowed"] is not False
        or row["release_auto_publish_allowed"] is not False
        or row["handoff_auto_apply_allowed"] is not False
        or row["real_world_actions_allowed"] is not False
    ]

    non_ready_rows = [row for row in rows if row["status"] != "ready"]

    if missing_items:
        handoff_status = "BLOCKED_MISSING_HANDOFF_ITEM"
    elif unsafe_rows:
        handoff_status = "BLOCKED_SAFETY_BOUNDARY_VIOLATION"
    elif non_ready_rows:
        handoff_status = "BLOCKED_NON_READY_ITEM"
    else:
        handoff_status = "READY_FOR_OPERATOR_BRANCH_HANDOFF"

    return {
        "ok": True,
        "type": "p14_final_branch_handoff_checkpoint",
        "current_stage": "P14-D52-D54",
        "branch_name": branch_name,
        "target_branch": target_branch,
        "latest_commit_label": latest_commit_label,
        "validation_passed_count": validation_passed_count,
        "handoff_status": handoff_status,
        "purpose": "final review-only branch handoff checkpoint before any later human-controlled merge or release",
        "required_handoff_items": list(REQUIRED_HANDOFF_ITEMS),
        "missing_items": missing_items,
        "unsafe_item_count": len(unsafe_rows),
        "unsafe_items": unsafe_rows,
        "non_ready_item_count": len(non_ready_rows),
        "non_ready_items": non_ready_rows,
        "rows": rows,
        "handoff_policy": {
            "operator_branch_handoff_required": True,
            "merge_to_main_allowed_now": False,
            "merge_auto_execute_allowed": False,
            "release_allowed_now": False,
            "release_auto_publish_allowed": False,
            "handoff_auto_apply_allowed": False,
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


def write_final_branch_handoff_checkpoint(
    branch_name: str,
    target_branch: str,
    latest_commit_label: str,
    validation_passed_count: int,
    handoff_items: list[dict[str, Any]],
    path: str | Path,
) -> dict[str, Any]:
    checkpoint = build_final_branch_handoff_checkpoint(
        branch_name=branch_name,
        target_branch=target_branch,
        latest_commit_label=latest_commit_label,
        validation_passed_count=validation_passed_count,
        handoff_items=handoff_items,
    )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(checkpoint, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p14_final_branch_handoff_checkpoint_written",
        "output_path": str(output),
        "checkpoint": checkpoint,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "merge_auto_execute_allowed": False,
        "release_auto_publish_allowed": False,
        "handoff_auto_apply_allowed": False,
        "real_world_actions_allowed": False,
    }
