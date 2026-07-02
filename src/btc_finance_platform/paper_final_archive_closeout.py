from typing import Any

P12_REQUIRED_DAYS = tuple(f"P12-D{i}" for i in range(1, 16))

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

def _missing_days(completed_days: list[str]) -> list[str]:
    completed = set(completed_days)
    return [day for day in P12_REQUIRED_DAYS if day not in completed]

def evaluate_p12_final_archive_closeout(
    release_package_summary: dict[str, Any],
    release_acceptance_summary: dict[str, Any],
    archive_manifest_summary: dict[str, Any],
    archive_acceptance_summary: dict[str, Any],
    completed_days: list[str],
) -> dict[str, Any]:
    if not isinstance(release_package_summary, dict):
        raise ValueError("release_package_summary must be a dict")
    if not isinstance(release_acceptance_summary, dict):
        raise ValueError("release_acceptance_summary must be a dict")
    if not isinstance(archive_manifest_summary, dict):
        raise ValueError("archive_manifest_summary must be a dict")
    if not isinstance(archive_acceptance_summary, dict):
        raise ValueError("archive_acceptance_summary must be a dict")
    if not isinstance(completed_days, list):
        raise ValueError("completed_days must be a list")

    missing = _missing_days(completed_days)
    reports = (release_package_summary, release_acceptance_summary, archive_manifest_summary, archive_acceptance_summary)

    checks = {
        "all_p12_days_completed": len(missing) == 0,
        "release_package_ready": release_package_summary.get("paper_final_release_ready") is True,
        "release_acceptance_accepted": release_acceptance_summary.get("paper_final_release_accepted") is True,
        "archive_manifest_ready": archive_manifest_summary.get("paper_final_release_archive_ready") is True,
        "archive_acceptance_accepted": archive_acceptance_summary.get("paper_archive_acceptance_accepted") is True,
        "all_reports_paper_only": all(item.get("paper_only") is True for item in reports),
        "operator_review_required": all(item.get("operator_review_required") is True for item in reports),
        "no_forbidden_real_action_flags": _no_forbidden_true(*reports),
    }

    blocked_reasons = [f"check_failed:{name}" for name, passed in checks.items() if not passed]
    completed = len(blocked_reasons) == 0

    return {
        "ok": True,
        "type": "p12_final_archive_closeout",
        "closeout_status": "completed" if completed else "blocked",
        "p12_completed": completed,
        "final_archive_completed": completed,
        "completed_day_count": len(set(completed_days)),
        "required_day_count": len(P12_REQUIRED_DAYS),
        "missing_days": missing,
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
        "next_stage_allowed": False,
        "next_stage": None,
    }

def summarize_p12_final_archive_closeout(closeout: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(closeout, dict):
        raise ValueError("closeout must be a dict")

    return {
        "ok": True,
        "type": "p12_final_archive_closeout_summary",
        "status": closeout.get("closeout_status"),
        "p12_completed": closeout.get("p12_completed") is True,
        "final_archive_completed": closeout.get("final_archive_completed") is True,
        "blocked_reasons": closeout.get("blocked_reasons", []),
        "paper_only": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "real_execution": False,
        "operator_review_required": True,
    }
