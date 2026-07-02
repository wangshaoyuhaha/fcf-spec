from typing import Any


REQUIRED_ACCEPTANCE_ITEMS = (
    "archive_manifest_reviewed",
    "archive_items_verified",
    "validation_record_verified",
    "paper_only_boundary_verified",
    "operator_review_record_verified",
    "final_archive_location_recorded",
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
        return value.strip().lower() in {"true", "yes", "1", "approved", "completed", "passed", "accepted", "verified"}
    return bool(value)


def _no_forbidden_true(*payloads: dict[str, Any]) -> bool:
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        for field in FORBIDDEN_TRUE_FIELDS:
            if _as_bool(payload.get(field)):
                return False
    return True


def build_paper_final_release_archive_acceptance_gate(
    archive_manifest_summary: dict[str, Any],
    acceptance_checklist: dict[str, Any],
    operator_record: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(archive_manifest_summary, dict):
        raise ValueError("archive_manifest_summary must be a dict")
    if not isinstance(acceptance_checklist, dict):
        raise ValueError("acceptance_checklist must be a dict")
    if not isinstance(operator_record, dict):
        raise ValueError("operator_record must be a dict")

    missing_items = [item for item in REQUIRED_ACCEPTANCE_ITEMS if not _as_bool(acceptance_checklist.get(item))]

    checks = {
        "archive_manifest_ready": archive_manifest_summary.get("paper_final_release_archive_ready") is True,
        "archive_manifest_paper_only": archive_manifest_summary.get("paper_only") is True,
        "acceptance_checklist_complete": len(missing_items) == 0,
        "operator_review_required": archive_manifest_summary.get("operator_review_required") is True,
        "operator_reviewed": _as_bool(operator_record.get("operator_reviewed")) is True,
        "operator_accepted": _as_bool(operator_record.get("operator_accepted")) is True,
        "no_forbidden_real_action_flags": _no_forbidden_true(archive_manifest_summary, acceptance_checklist, operator_record),
    }

    blocked_reasons = [f"check_failed:{name}" for name, passed in checks.items() if not passed]
    accepted = len(blocked_reasons) == 0

    return {
        "ok": True,
        "type": "paper_final_release_archive_acceptance_gate",
        "acceptance_status": "accepted" if accepted else "blocked",
        "paper_archive_acceptance_accepted": accepted,
        "missing_acceptance_items": missing_items,
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


def summarize_paper_final_release_archive_acceptance(gate: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(gate, dict):
        raise ValueError("gate must be a dict")

    return {
        "ok": True,
        "type": "paper_final_release_archive_acceptance_summary",
        "status": gate.get("acceptance_status"),
        "paper_archive_acceptance_accepted": gate.get("paper_archive_acceptance_accepted") is True,
        "missing_acceptance_items": gate.get("missing_acceptance_items", []),
        "blocked_reasons": gate.get("blocked_reasons", []),
        "paper_only": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "real_execution": False,
        "operator_review_required": True,
    }
