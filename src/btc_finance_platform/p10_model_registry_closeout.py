from typing import Any


P10_REQUIRED_DAYS = tuple(f"P10-D{i}" for i in range(1, 16))

REQUIRED_FALSE_FIELDS = (
    "real_world_actions_allowed",
    "deployment_allowed_now",
    "parameter_update_allowed_now",
)

REAL_ACTION_FIELDS = (
    "real_exchange_api",
    "real_brokerage_api",
    "real_api_key_required",
    "wallet_private_key_required",
    "real_order",
    "real_execution",
    "real_balance",
    "real_position",
    "real_money_impact",
)


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "approved", "completed"}
    return bool(value)


def _required_false(payload: dict[str, Any], field: str) -> bool:
    return field in payload and _as_bool(payload.get(field)) is False


def _no_real_action_flags(payload: dict[str, Any]) -> bool:
    return not any(_as_bool(payload.get(field)) for field in REAL_ACTION_FIELDS)


def _missing_days(completed_days: list[str]) -> list[str]:
    completed = set(completed_days)
    return [day for day in P10_REQUIRED_DAYS if day not in completed]


def evaluate_p10_model_registry_closeout(
    registry_report: dict[str, Any],
    readiness_report: dict[str, Any],
    completed_days: list[str],
) -> dict[str, Any]:
    if not isinstance(registry_report, dict):
        raise ValueError("registry_report must be a dict")
    if not isinstance(readiness_report, dict):
        raise ValueError("readiness_report must be a dict")
    if not isinstance(completed_days, list):
        raise ValueError("completed_days must be a list")

    missing = _missing_days(completed_days)

    checks = {
        "all_p10_days_completed": len(missing) == 0,
        "registry_report_paper_only": registry_report.get("paper_only") is True,
        "readiness_report_paper_only": readiness_report.get("paper_only") is True,
        "registry_report_operator_review_required": registry_report.get("operator_review_required") is True,
        "readiness_report_operator_review_required": readiness_report.get("operator_review_required") is True,
        "registry_report_no_real_action_flags": _no_real_action_flags(registry_report),
        "readiness_report_no_real_action_flags": _no_real_action_flags(readiness_report),
        "registry_report_no_real_world_allowance": all(_required_false(registry_report, field) for field in REQUIRED_FALSE_FIELDS),
        "readiness_report_no_real_world_allowance": all(_required_false(readiness_report, field) for field in REQUIRED_FALSE_FIELDS),
        "registry_report_no_bypass_operator_review": not _as_bool(registry_report.get("bypass_operator_review")),
        "readiness_report_no_bypass_operator_review": not _as_bool(readiness_report.get("bypass_operator_review")),
        "registry_report_no_bypass_policy_risk": not _as_bool(registry_report.get("bypass_policy_risk_safe_boundary")),
        "readiness_report_no_bypass_policy_risk": not _as_bool(readiness_report.get("bypass_policy_risk_safe_boundary")),
    }

    blocked_reasons = [f"check_failed:{name}" for name, passed in checks.items() if not passed]
    completed = len(blocked_reasons) == 0

    return {
        "ok": True,
        "type": "p10_model_registry_closeout",
        "closeout_status": "completed" if completed else "blocked",
        "p10_completed": completed,
        "completed_day_count": len(set(completed_days)),
        "required_day_count": len(P10_REQUIRED_DAYS),
        "missing_days": missing,
        "paper_only": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
        "real_exchange_api": False,
        "real_brokerage_api": False,
        "real_api_key_required": False,
        "wallet_private_key_required": False,
        "real_order": False,
        "real_execution": False,
        "real_balance": False,
        "real_position": False,
        "real_money_impact": False,
        "operator_review_required": True,
        "checks": checks,
        "blocked_reasons": blocked_reasons,
        "next_stage_allowed": completed,
        "next_stage": "P11" if completed else None,
    }


def build_p10_model_registry_closeout_summary(closeout: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(closeout, dict):
        raise ValueError("closeout must be a dict")

    return {
        "ok": True,
        "type": "p10_model_registry_closeout_summary",
        "status": closeout.get("closeout_status"),
        "p10_completed": closeout.get("p10_completed") is True,
        "next_stage_allowed": closeout.get("next_stage_allowed") is True,
        "next_stage": closeout.get("next_stage"),
        "blocked_reasons": closeout.get("blocked_reasons", []),
        "paper_only": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
        "operator_review_required": True,
    }
