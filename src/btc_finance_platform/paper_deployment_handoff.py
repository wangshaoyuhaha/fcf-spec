from typing import Any


REQUIRED_APPROVAL_FIELDS = (
    "operator_review_required",
    "operator_approved",
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
        return value.strip().lower() in {"true", "yes", "1", "approved", "completed"}
    return bool(value)


def build_paper_deployment_handoff_pack(
    model_id: str,
    registry_closeout: dict[str, Any],
    readiness_summary: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(model_id, str) or not model_id.strip():
        raise ValueError("model_id must be a non-empty string")
    if not isinstance(registry_closeout, dict):
        raise ValueError("registry_closeout must be a dict")
    if not isinstance(readiness_summary, dict):
        raise ValueError("readiness_summary must be a dict")

    checks = {
        "p10_closeout_completed": registry_closeout.get("p10_completed") is True,
        "readiness_next_stage_allowed": readiness_summary.get("next_stage_allowed") is True,
        "paper_only": registry_closeout.get("paper_only") is True and readiness_summary.get("paper_only") is True,
        "operator_review_required": registry_closeout.get("operator_review_required") is True and readiness_summary.get("operator_review_required") is True,
        "operator_approved": readiness_summary.get("operator_approved") is True,
        "no_forbidden_real_action_flags": not any(_as_bool(registry_closeout.get(field)) or _as_bool(readiness_summary.get(field)) for field in FORBIDDEN_TRUE_FIELDS),
    }

    blocked_reasons = [f"check_failed:{name}" for name, passed in checks.items() if not passed]
    handoff_ready = len(blocked_reasons) == 0

    return {
        "ok": True,
        "type": "paper_deployment_handoff_pack",
        "model_id": model_id.strip(),
        "handoff_status": "ready" if handoff_ready else "blocked",
        "paper_deployment_handoff_ready": handoff_ready,
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


def summarize_paper_deployment_handoff(pack: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(pack, dict):
        raise ValueError("pack must be a dict")

    return {
        "ok": True,
        "type": "paper_deployment_handoff_summary",
        "model_id": pack.get("model_id"),
        "status": pack.get("handoff_status"),
        "paper_deployment_handoff_ready": pack.get("paper_deployment_handoff_ready") is True,
        "blocked_reasons": pack.get("blocked_reasons", []),
        "paper_only": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "operator_review_required": True,
    }
