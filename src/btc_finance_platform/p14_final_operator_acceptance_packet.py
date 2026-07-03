import json
from pathlib import Path
from typing import Any


REQUIRED_ACCEPTANCE_ITEMS = (
    "p14_learning_engine_closeout",
    "p14_merge_readiness_bridge",
    "all_checks_passed",
    "pytest_passed",
    "repo_clean",
    "operator_review_required",
    "paper_only_boundary_preserved",
)


def normalize_acceptance_item(item: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise ValueError("acceptance item must be a dict")

    item_key = item.get("item_key")
    if not item_key:
        raise ValueError("item_key is required")

    return {
        "item_key": str(item_key),
        "status": str(item.get("status", "accepted")),
        "operator_review_required": bool(item.get("operator_review_required", True)),
        "manual_decision_required": bool(item.get("manual_decision_required", True)),
        "merge_auto_execute_allowed": bool(item.get("merge_auto_execute_allowed", False)),
        "release_auto_publish_allowed": bool(item.get("release_auto_publish_allowed", False)),
        "real_world_actions_allowed": bool(item.get("real_world_actions_allowed", False)),
    }


def default_operator_acceptance_items() -> list[dict[str, Any]]:
    return [
        {"item_key": "p14_learning_engine_closeout", "status": "accepted"},
        {"item_key": "p14_merge_readiness_bridge", "status": "accepted"},
        {"item_key": "all_checks_passed", "status": "accepted"},
        {"item_key": "pytest_passed", "status": "accepted"},
        {"item_key": "repo_clean", "status": "accepted"},
        {"item_key": "operator_review_required", "status": "accepted"},
        {"item_key": "paper_only_boundary_preserved", "status": "accepted"},
    ]


def build_final_operator_acceptance_packet(
    source_branch: str,
    target_branch: str,
    acceptance_items: list[dict[str, Any]],
    validation_passed_count: int,
) -> dict[str, Any]:
    if not source_branch:
        raise ValueError("source_branch is required")

    if not target_branch:
        raise ValueError("target_branch is required")

    if source_branch == target_branch:
        raise ValueError("source_branch and target_branch must differ")

    if not isinstance(validation_passed_count, int) or validation_passed_count <= 0:
        raise ValueError("validation_passed_count must be a positive integer")

    if not isinstance(acceptance_items, list):
        raise ValueError("acceptance_items must be a list")

    rows = [normalize_acceptance_item(item) for item in acceptance_items]
    present = {row["item_key"] for row in rows}
    missing_items = [key for key in REQUIRED_ACCEPTANCE_ITEMS if key not in present]

    unsafe_rows = [
        row for row in rows
        if row["operator_review_required"] is not True
        or row["manual_decision_required"] is not True
        or row["merge_auto_execute_allowed"] is not False
        or row["release_auto_publish_allowed"] is not False
        or row["real_world_actions_allowed"] is not False
    ]

    non_accepted_rows = [row for row in rows if row["status"] != "accepted"]

    if missing_items:
        acceptance_status = "BLOCKED_MISSING_ACCEPTANCE_ITEM"
    elif unsafe_rows:
        acceptance_status = "BLOCKED_SAFETY_BOUNDARY_VIOLATION"
    elif non_accepted_rows:
        acceptance_status = "BLOCKED_NON_ACCEPTED_ITEM"
    else:
        acceptance_status = "READY_FOR_FINAL_OPERATOR_ACCEPTANCE"

    return {
        "ok": True,
        "type": "p14_final_operator_acceptance_packet",
        "current_stage": "P14-D46-D48",
        "source_branch": source_branch,
        "target_branch": target_branch,
        "validation_passed_count": validation_passed_count,
        "acceptance_status": acceptance_status,
        "purpose": "final review-only operator acceptance packet before any later human-controlled merge or release decision",
        "required_acceptance_items": list(REQUIRED_ACCEPTANCE_ITEMS),
        "missing_items": missing_items,
        "unsafe_item_count": len(unsafe_rows),
        "unsafe_items": unsafe_rows,
        "non_accepted_item_count": len(non_accepted_rows),
        "non_accepted_items": non_accepted_rows,
        "rows": rows,
        "acceptance_policy": {
            "final_operator_acceptance_required": True,
            "merge_to_main_allowed_now": False,
            "merge_auto_execute_allowed": False,
            "release_allowed_now": False,
            "release_auto_publish_allowed": False,
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


def write_final_operator_acceptance_packet(
    source_branch: str,
    target_branch: str,
    acceptance_items: list[dict[str, Any]],
    validation_passed_count: int,
    path: str | Path,
) -> dict[str, Any]:
    packet = build_final_operator_acceptance_packet(
        source_branch=source_branch,
        target_branch=target_branch,
        acceptance_items=acceptance_items,
        validation_passed_count=validation_passed_count,
    )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p14_final_operator_acceptance_packet_written",
        "output_path": str(output),
        "packet": packet,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "merge_auto_execute_allowed": False,
        "release_auto_publish_allowed": False,
        "real_world_actions_allowed": False,
    }
