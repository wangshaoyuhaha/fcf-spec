from typing import Any


REQUIRED_ARCHIVE_ITEMS = (
    "project_state",
    "release_package_summary",
    "acceptance_summary",
    "validation_log",
    "safety_boundary_record",
    "operator_review_record",
)

FORBIDDEN_TRUE_FIELDS = (
    "real_exchange_api",
    "real_brokerage_api",
    "real_api_key_required",
    "wallet_private_key_required",
    "real_order",
    "real_execution",
    "real_balance",
    "real_position",
    "real_money_impact",
    "real_world_actions_allowed",
    "deployment_allowed_now",
    "parameter_update_allowed_now",
    "bypass_operator_review",
    "bypass_policy_risk_safe_boundary",
)


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "approved", "completed", "passed", "accepted"}
    return bool(value)


def _no_forbidden_true(*payloads: dict[str, Any]) -> bool:
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        for field in FORBIDDEN_TRUE_FIELDS:
            if _as_bool(payload.get(field)):
                return False
    return True


def build_paper_final_release_archive_manifest(
    acceptance_summary: dict[str, Any],
    archive_items: list[str],
    validation_record: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(acceptance_summary, dict):
        raise ValueError("acceptance_summary must be a dict")
    if not isinstance(archive_items, list):
        raise ValueError("archive_items must be a list")
    if not isinstance(validation_record, dict):
        raise ValueError("validation_record must be a dict")

    missing_items = [item for item in REQUIRED_ARCHIVE_ITEMS if item not in archive_items]

    checks = {
        "acceptance_completed": acceptance_summary.get("paper_final_release_accepted") is True,
        "acceptance_paper_only": acceptance_summary.get("paper_only") is True,
        "archive_items_complete": len(missing_items) == 0,
        "validation_passed": validation_record.get("all_checks_passed") is True and validation_record.get("pytest_passed") is True,
        "validation_paper_only": validation_record.get("paper_only") is True,
        "operator_review_required": acceptance_summary.get("operator_review_required") is True and validation_record.get("operator_review_required") is True,
        "no_forbidden_real_action_flags": _no_forbidden_true(acceptance_summary, validation_record),
    }

    blocked_reasons = [f"check_failed:{name}" for name, passed in checks.items() if not passed]
    ready = len(blocked_reasons) == 0

    return {
        "ok": True,
        "type": "paper_final_release_archive_manifest",
        "archive_status": "ready" if ready else "blocked",
        "paper_final_release_archive_ready": ready,
        "required_archive_items": list(REQUIRED_ARCHIVE_ITEMS),
        "provided_archive_items": archive_items,
        "missing_archive_items": missing_items,
        "paper_only": True,
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
        "parameter_update_allowed_now": False,
        "operator_review_required": True,
        "checks": checks,
        "blocked_reasons": blocked_reasons,
    }


def summarize_paper_final_release_archive_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be a dict")

    return {
        "ok": True,
        "type": "paper_final_release_archive_manifest_summary",
        "status": manifest.get("archive_status"),
        "paper_final_release_archive_ready": manifest.get("paper_final_release_archive_ready") is True,
        "missing_archive_items": manifest.get("missing_archive_items", []),
        "blocked_reasons": manifest.get("blocked_reasons", []),
        "paper_only": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "real_execution": False,
        "operator_review_required": True,
    }
