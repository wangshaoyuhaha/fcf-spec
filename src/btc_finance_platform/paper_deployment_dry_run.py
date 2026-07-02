from typing import Any


REQUIRED_DRY_RUN_STEPS = (
    "load_paper_handoff_pack",
    "verify_paper_preflight_gate",
    "simulate_config_render",
    "simulate_operator_review_checkpoint",
    "simulate_rollback_checkpoint",
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


def build_paper_deployment_dry_run_plan(
    preflight_summary: dict[str, Any],
    dry_run_steps: list[str],
    runtime_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(preflight_summary, dict):
        raise ValueError("preflight_summary must be a dict")
    if not isinstance(dry_run_steps, list):
        raise ValueError("dry_run_steps must be a list")
    if runtime_context is None:
        runtime_context = {}
    if not isinstance(runtime_context, dict):
        raise ValueError("runtime_context must be a dict")

    missing_steps = [step for step in REQUIRED_DRY_RUN_STEPS if step not in dry_run_steps]

    checks = {
        "preflight_passed": preflight_summary.get("paper_preflight_passed") is True,
        "preflight_paper_only": preflight_summary.get("paper_only") is True,
        "operator_review_required": preflight_summary.get("operator_review_required") is True,
        "dry_run_steps_complete": len(missing_steps) == 0,
        "runtime_context_paper_only": runtime_context.get("paper_only", True) is True,
        "no_forbidden_real_action_flags": _no_forbidden_true(preflight_summary, runtime_context),
    }

    blocked_reasons = [f"check_failed:{name}" for name, passed in checks.items() if not passed]
    dry_run_ready = len(blocked_reasons) == 0

    return {
        "ok": True,
        "type": "paper_deployment_dry_run_plan",
        "dry_run_status": "ready" if dry_run_ready else "blocked",
        "paper_dry_run_ready": dry_run_ready,
        "required_steps": list(REQUIRED_DRY_RUN_STEPS),
        "provided_steps": dry_run_steps,
        "missing_steps": missing_steps,
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


def summarize_paper_deployment_dry_run(plan: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(plan, dict):
        raise ValueError("plan must be a dict")

    return {
        "ok": True,
        "type": "paper_deployment_dry_run_summary",
        "status": plan.get("dry_run_status"),
        "paper_dry_run_ready": plan.get("paper_dry_run_ready") is True,
        "missing_steps": plan.get("missing_steps", []),
        "blocked_reasons": plan.get("blocked_reasons", []),
        "paper_only": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "real_execution": False,
        "operator_review_required": True,
    }
