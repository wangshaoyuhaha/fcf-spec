import json
from pathlib import Path
from typing import Any


REQUIRED_PLAN_ITEMS = (
    "final_branch_handoff_checkpoint",
    "final_archive_manifest",
    "final_operator_acceptance_packet",
    "all_checks_passed",
    "pytest_passed",
    "repo_clean",
    "human_operator_required",
)


def normalize_merge_plan_item(item: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise ValueError("merge plan item must be a dict")

    item_key = item.get("item_key")
    if not item_key:
        raise ValueError("item_key is required")

    return {
        "item_key": str(item_key),
        "status": str(item.get("status", "ready")),
        "human_operator_required": bool(item.get("human_operator_required", True)),
        "auto_execute_allowed": bool(item.get("auto_execute_allowed", False)),
        "auto_merge_allowed": bool(item.get("auto_merge_allowed", False)),
        "auto_release_allowed": bool(item.get("auto_release_allowed", False)),
        "real_world_actions_allowed": bool(item.get("real_world_actions_allowed", False)),
    }


def default_human_merge_plan_items() -> list[dict[str, Any]]:
    return [
        {"item_key": "final_branch_handoff_checkpoint", "status": "ready"},
        {"item_key": "final_archive_manifest", "status": "ready"},
        {"item_key": "final_operator_acceptance_packet", "status": "ready"},
        {"item_key": "all_checks_passed", "status": "ready"},
        {"item_key": "pytest_passed", "status": "ready"},
        {"item_key": "repo_clean", "status": "ready"},
        {"item_key": "human_operator_required", "status": "ready"},
    ]


def default_manual_merge_commands(source_branch: str, target_branch: str) -> list[str]:
    if not source_branch:
        raise ValueError("source_branch is required")

    if not target_branch:
        raise ValueError("target_branch is required")

    if source_branch == target_branch:
        raise ValueError("source_branch and target_branch must differ")

    return [
        "git status --short",
        "python scripts/run_all_checks.py",
        "python -m pytest -q",
        f"git checkout {target_branch}",
        f"git pull origin {target_branch}",
        f"git merge --no-ff {source_branch}",
        "python scripts/run_all_checks.py",
        "python -m pytest -q",
        f"git push origin {target_branch}",
    ]


def build_human_merge_plan_packet(
    source_branch: str,
    target_branch: str,
    validation_passed_count: int,
    plan_items: list[dict[str, Any]],
) -> dict[str, Any]:
    if not source_branch:
        raise ValueError("source_branch is required")

    if not target_branch:
        raise ValueError("target_branch is required")

    if source_branch == target_branch:
        raise ValueError("source_branch and target_branch must differ")

    if not isinstance(validation_passed_count, int) or validation_passed_count <= 0:
        raise ValueError("validation_passed_count must be a positive integer")

    if not isinstance(plan_items, list):
        raise ValueError("plan_items must be a list")

    rows = [normalize_merge_plan_item(item) for item in plan_items]
    present = {row["item_key"] for row in rows}
    missing_items = [key for key in REQUIRED_PLAN_ITEMS if key not in present]

    unsafe_rows = [
        row for row in rows
        if row["human_operator_required"] is not True
        or row["auto_execute_allowed"] is not False
        or row["auto_merge_allowed"] is not False
        or row["auto_release_allowed"] is not False
        or row["real_world_actions_allowed"] is not False
    ]

    non_ready_rows = [row for row in rows if row["status"] != "ready"]

    if missing_items:
        plan_status = "BLOCKED_MISSING_PLAN_ITEM"
    elif unsafe_rows:
        plan_status = "BLOCKED_SAFETY_BOUNDARY_VIOLATION"
    elif non_ready_rows:
        plan_status = "BLOCKED_NON_READY_ITEM"
    else:
        plan_status = "READY_FOR_HUMAN_MERGE_REVIEW"

    return {
        "ok": True,
        "type": "p14_human_merge_plan_packet",
        "current_stage": "P14-D55-D57",
        "source_branch": source_branch,
        "target_branch": target_branch,
        "validation_passed_count": validation_passed_count,
        "plan_status": plan_status,
        "purpose": "review-only manual merge plan packet; commands are documented but not executed",
        "manual_commands": default_manual_merge_commands(source_branch, target_branch),
        "required_plan_items": list(REQUIRED_PLAN_ITEMS),
        "missing_items": missing_items,
        "unsafe_item_count": len(unsafe_rows),
        "unsafe_items": unsafe_rows,
        "non_ready_item_count": len(non_ready_rows),
        "non_ready_items": non_ready_rows,
        "rows": rows,
        "merge_plan_policy": {
            "manual_merge_plan_only": True,
            "merge_to_main_allowed_now": False,
            "auto_execute_allowed": False,
            "auto_merge_allowed": False,
            "auto_release_allowed": False,
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


def write_human_merge_plan_packet(
    source_branch: str,
    target_branch: str,
    validation_passed_count: int,
    plan_items: list[dict[str, Any]],
    path: str | Path,
) -> dict[str, Any]:
    packet = build_human_merge_plan_packet(
        source_branch=source_branch,
        target_branch=target_branch,
        validation_passed_count=validation_passed_count,
        plan_items=plan_items,
    )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p14_human_merge_plan_packet_written",
        "output_path": str(output),
        "packet": packet,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "auto_execute_allowed": False,
        "auto_merge_allowed": False,
        "auto_release_allowed": False,
        "real_world_actions_allowed": False,
    }
