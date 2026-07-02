from typing import Any


REQUIRED_OBSERVATIONS = (
    "handoff_pack_loaded",
    "preflight_gate_verified",
    "config_render_simulated",
    "operator_checkpoint_simulated",
    "rollback_checkpoint_simulated",
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
        return value.strip().lower() in {"true", "yes", "1", "approved", "completed", "passed"}
    return bool(value)


def _no_forbidden_true(*payloads: dict[str, Any]) -> bool:
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        for field in FORBIDDEN_TRUE_FIELDS:
            if _as_bool(payload.get(field)):
                return False
    return True


def build_paper_deployment_dry_run_report(
    dry_run_plan: dict[str, Any],
    observations: dict[str, Any],
    operator_review: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(dry_run_plan, dict):
        raise ValueError("dry_run_plan must be a dict")
    if not isinstance(observations, dict):
        raise ValueError("observations must be a dict")
    if not isinstance(operator_review, dict):
        raise ValueError("operator_review must be a dict")

    missing_observations = [item for item in REQUIRED_OBSERVATIONS if not _as_bool(observations.get(item))]

    checks = {
        "dry_run_plan_ready": dry_run_plan.get("paper_dry_run_ready") is True,
        "dry_run_plan_paper_only": dry_run_plan.get("paper_only") is True,
        "observations_complete": len(missing_observations) == 0,
        "operator_review_required": dry_run_plan.get("operator_review_required") is True,
        "operator_review_recorded": _as_bool(operator_review.get("operator_reviewed")) is True,
        "operator_approved": _as_bool(operator_review.get("operator_approved")) is True,
        "no_forbidden_real_action_flags": _no_forbidden_true(dry_run_plan, observations, operator_review),
    }

    blocked_reasons = [f"check_failed:{name}" for name, passed in checks.items() if not passed]
    report_ready = len(blocked_reasons) == 0

    return {
        "ok": True,
        "type": "paper_deployment_dry_run_report",
        "report_status": "accepted" if report_ready else "blocked",
        "paper_dry_run_report_accepted": report_ready,
        "missing_observations": missing_observations,
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


def summarize_paper_deployment_dry_run_report(report: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(report, dict):
        raise ValueError("report must be a dict")

    return {
        "ok": True,
        "type": "paper_deployment_dry_run_report_summary",
        "status": report.get("report_status"),
        "paper_dry_run_report_accepted": report.get("paper_dry_run_report_accepted") is True,
        "missing_observations": report.get("missing_observations", []),
        "blocked_reasons": report.get("blocked_reasons", []),
        "paper_only": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "real_execution": False,
        "operator_review_required": True,
    }
