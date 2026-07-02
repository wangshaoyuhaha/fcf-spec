from typing import Any


P11_REQUIRED_DAYS = tuple(f"P11-D{i}" for i in range(1, 16))

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


def _missing_days(completed_days: list[str]) -> list[str]:
    completed = set(completed_days)
    return [day for day in P11_REQUIRED_DAYS if day not in completed]


def evaluate_p11_paper_deployment_closeout(
    handoff_summary: dict[str, Any],
    preflight_summary: dict[str, Any],
    dry_run_summary: dict[str, Any],
    dry_run_report_summary: dict[str, Any],
    completed_days: list[str],
) -> dict[str, Any]:
    if not isinstance(handoff_summary, dict):
        raise ValueError("handoff_summary must be a dict")
    if not isinstance(preflight_summary, dict):
        raise ValueError("preflight_summary must be a dict")
    if not isinstance(dry_run_summary, dict):
        raise ValueError("dry_run_summary must be a dict")
    if not isinstance(dry_run_report_summary, dict):
        raise ValueError("dry_run_report_summary must be a dict")
    if not isinstance(completed_days, list):
        raise ValueError("completed_days must be a list")

    missing = _missing_days(completed_days)

    checks = {
        "all_p11_days_completed": len(missing) == 0,
        "handoff_ready": handoff_summary.get("paper_deployment_handoff_ready") is True,
        "preflight_passed": preflight_summary.get("paper_preflight_passed") is True,
        "dry_run_ready": dry_run_summary.get("paper_dry_run_ready") is True,
        "dry_run_report_accepted": dry_run_report_summary.get("paper_dry_run_report_accepted") is True,
        "all_reports_paper_only": all(report.get("paper_only") is True for report in (handoff_summary, preflight_summary, dry_run_summary, dry_run_report_summary)),
        "operator_review_required": all(report.get("operator_review_required") is True for report in (handoff_summary, preflight_summary, dry_run_summary, dry_run_report_summary)),
        "no_forbidden_real_action_flags": _no_forbidden_true(handoff_summary, preflight_summary, dry_run_summary, dry_run_report_summary),
    }

    blocked_reasons = [f"check_failed:{name}" for name, passed in checks.items() if not passed]
    completed = len(blocked_reasons) == 0

    return {
        "ok": True,
        "type": "p11_paper_deployment_closeout",
        "closeout_status": "completed" if completed else "blocked",
        "p11_completed": completed,
        "completed_day_count": len(set(completed_days)),
        "required_day_count": len(P11_REQUIRED_DAYS),
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
        "next_stage_allowed": completed,
        "next_stage": "P12" if completed else None,
    }


def summarize_p11_paper_deployment_closeout(closeout: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(closeout, dict):
        raise ValueError("closeout must be a dict")

    return {
        "ok": True,
        "type": "p11_paper_deployment_closeout_summary",
        "status": closeout.get("closeout_status"),
        "p11_completed": closeout.get("p11_completed") is True,
        "next_stage_allowed": closeout.get("next_stage_allowed") is True,
        "next_stage": closeout.get("next_stage"),
        "blocked_reasons": closeout.get("blocked_reasons", []),
        "paper_only": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "real_execution": False,
        "operator_review_required": True,
    }
