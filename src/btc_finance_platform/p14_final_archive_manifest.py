import json
from pathlib import Path
from typing import Any


REQUIRED_ARCHIVE_ITEMS = (
    "p14_learning_engine_closeout",
    "p14_merge_readiness_bridge",
    "p14_final_operator_acceptance_packet",
    "all_checks_passed",
    "pytest_passed",
    "repo_clean",
    "paper_only_boundary_preserved",
)


def normalize_archive_item(item: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise ValueError("archive item must be a dict")

    item_key = item.get("item_key")
    if not item_key:
        raise ValueError("item_key is required")

    return {
        "item_key": str(item_key),
        "status": str(item.get("status", "archived")),
        "operator_review_required": bool(item.get("operator_review_required", True)),
        "merge_auto_execute_allowed": bool(item.get("merge_auto_execute_allowed", False)),
        "release_auto_publish_allowed": bool(item.get("release_auto_publish_allowed", False)),
        "archive_auto_publish_allowed": bool(item.get("archive_auto_publish_allowed", False)),
        "real_world_actions_allowed": bool(item.get("real_world_actions_allowed", False)),
    }


def default_final_archive_items() -> list[dict[str, Any]]:
    return [
        {"item_key": "p14_learning_engine_closeout", "status": "archived"},
        {"item_key": "p14_merge_readiness_bridge", "status": "archived"},
        {"item_key": "p14_final_operator_acceptance_packet", "status": "archived"},
        {"item_key": "all_checks_passed", "status": "archived"},
        {"item_key": "pytest_passed", "status": "archived"},
        {"item_key": "repo_clean", "status": "archived"},
        {"item_key": "paper_only_boundary_preserved", "status": "archived"},
    ]


def build_final_archive_manifest(
    source_branch: str,
    target_branch: str,
    validation_passed_count: int,
    archive_items: list[dict[str, Any]],
) -> dict[str, Any]:
    if not source_branch:
        raise ValueError("source_branch is required")

    if not target_branch:
        raise ValueError("target_branch is required")

    if source_branch == target_branch:
        raise ValueError("source_branch and target_branch must differ")

    if not isinstance(validation_passed_count, int) or validation_passed_count <= 0:
        raise ValueError("validation_passed_count must be a positive integer")

    if not isinstance(archive_items, list):
        raise ValueError("archive_items must be a list")

    rows = [normalize_archive_item(item) for item in archive_items]
    present = {row["item_key"] for row in rows}
    missing_items = [key for key in REQUIRED_ARCHIVE_ITEMS if key not in present]

    unsafe_rows = [
        row for row in rows
        if row["operator_review_required"] is not True
        or row["merge_auto_execute_allowed"] is not False
        or row["release_auto_publish_allowed"] is not False
        or row["archive_auto_publish_allowed"] is not False
        or row["real_world_actions_allowed"] is not False
    ]

    non_archived_rows = [row for row in rows if row["status"] != "archived"]

    if missing_items:
        archive_status = "BLOCKED_MISSING_ARCHIVE_ITEM"
    elif unsafe_rows:
        archive_status = "BLOCKED_SAFETY_BOUNDARY_VIOLATION"
    elif non_archived_rows:
        archive_status = "BLOCKED_NON_ARCHIVED_ITEM"
    else:
        archive_status = "READY_FOR_FINAL_OPERATOR_ARCHIVE_REVIEW"

    return {
        "ok": True,
        "type": "p14_final_archive_manifest",
        "current_stage": "P14-D49-D51",
        "source_branch": source_branch,
        "target_branch": target_branch,
        "validation_passed_count": validation_passed_count,
        "archive_status": archive_status,
        "purpose": "final review-only P14 archive manifest before any later human-controlled merge or release",
        "required_archive_items": list(REQUIRED_ARCHIVE_ITEMS),
        "missing_items": missing_items,
        "unsafe_item_count": len(unsafe_rows),
        "unsafe_items": unsafe_rows,
        "non_archived_item_count": len(non_archived_rows),
        "non_archived_items": non_archived_rows,
        "rows": rows,
        "archive_policy": {
            "final_operator_archive_review_required": True,
            "merge_to_main_allowed_now": False,
            "merge_auto_execute_allowed": False,
            "release_allowed_now": False,
            "release_auto_publish_allowed": False,
            "archive_auto_publish_allowed": False,
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


def write_final_archive_manifest(
    source_branch: str,
    target_branch: str,
    validation_passed_count: int,
    archive_items: list[dict[str, Any]],
    path: str | Path,
) -> dict[str, Any]:
    manifest = build_final_archive_manifest(
        source_branch=source_branch,
        target_branch=target_branch,
        validation_passed_count=validation_passed_count,
        archive_items=archive_items,
    )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "p14_final_archive_manifest_written",
        "output_path": str(output),
        "manifest": manifest,
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "merge_auto_execute_allowed": False,
        "release_auto_publish_allowed": False,
        "archive_auto_publish_allowed": False,
        "real_world_actions_allowed": False,
    }
