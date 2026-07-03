import json
from pathlib import Path
from typing import Any


REQUIRED_CLOSEOUTS = (
    "p13_operator_console_closeout",
    "p14_learning_engine_closeout",
)


def normalize_readiness_item(item: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise ValueError("readiness item must be a dict")

    item_key = item.get("item_key")
    if not item_key:
        raise ValueError("item_key is required")

    return {
        "item_key": str(item_key),
        "status": str(item.get("status", "ready")),
        "operator_review_required": bool(item.get("operator_review_required", True)),
        "merge_auto_apply_allowed": bool(item.get("merge_auto_apply_allowed", False)),
        "release_auto_publish_allowed": bool(item.get("release_auto_publish_allowed", False)),
        "real_world_actions_allowed": bool(item.get("real_world_actions_allowed", False)),
    }


def default_merge_readiness_items() -> list[dict[str, Any]]:
    return [
        {"item_key": "p13_operator_console_closeout", "status": "ready"},
        {"item_key": "p14_learning_engine_closeout", "status": "ready"},
        {"item_key": "all_checks_passed", "status": "ready"},
        {"item_key": "pytest_passed", "status": "ready"},
        {"item_key": "repo_clean_before_merge_review", "status": "ready"},
        {"item_key": "paper_only_boundary_preserved", "status": "ready"},
        {"item_key": "operator_review_required", "status": "ready"},
    ]


def build_merge_readiness_bridge(
    source_branch: str,
    target_branch: str,
    readiness_items: list[dict[str, Any]],
) -> dict[str, Any]:
    if not source_branch:
        raise ValueError("source_branch is required")

    if not target_branch:
        raise ValueError("target_branch is required")

    if source_branch == target_branch:
        raise ValueError("source_branch and target_branch must differ")

    if not isinstance(readiness_items, list):
        raise ValueError("readiness_items must be a list")

    rows = [normalize_readiness_item(item) for item in readiness_items]
    present = {row["item_key"] for row in rows}
    missing_closeouts = [key for key in REQUIRED_CLOSEOUTS if key not in present]

    unsafe_rows = [
        row for row in rows
        if row["operator_review_required"] is not True
        or row["merge_auto_apply_allowed"] is not False
        or row["release_auto_publish_allowed"] is not False
        or row["real_world_actions_allowed"] is not False
    ]

    non_ready_rows = [row for row in rows if row["status"] != "ready"]

    if missing_closeouts:
        readiness_status = "BLOCKED_MISSING_CLOSEOUT"
    elif unsafe_rows:
        readiness_status = "BLOCKED_SAFETY_BOUNDARY_VIOLATION"
    elif non_ready_rows:
        readiness_status = "BLOCKED_NON_READY_ITEM"
    else:
        readiness_status = "READY_FOR_OPERATOR_MERGE_REVIEW"

    return {
        "ok": True,
        "type": "p14_merge_readiness_bridge",
        "current_stage": "P14-D43-D45",
        "source_branch": source_branch,
        "target_branch": target_branch,
        "readiness_status": readiness_status,
        "purpose": "prepare a review-only bridge before any later merge to main",
        "required_closeouts": list(REQUIRED_CLOSEOUTS),
        "missing_closeouts": missing_closeouts,
        "unsafe_item_count": len(unsafe_rows),
        "unsafe_items": unsafe_rows,
        "non_ready_item_count": len(non_ready_rows),
        "non_ready_items": non_ready_rows,
        "rows": rows,
        "merge_policy": {
            "merge_to_main_allowed_now": False,
            "merge_auto_apply_allowed": False,
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


def write_merge_readiness_bridge(
    source_branch: str,
    target_branch: str,
    readiness_items: list[dict[str, Any]],
    path: str | Path,
) -> dict[str, Any]:
    report = build_merge_readiness_bridge(source_branch, target_branch, readiness_items)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p14_merge_readiness_bridge_written",
        "output_path": str(output),
        "report": report,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "merge_auto_apply_allowed": False,
        "release_auto_publish_allowed": False,
        "real_world_actions_allowed": False,
    }
