from typing import Any


REQUIRED_CHECKLIST_ITEMS = (
    "paper_handoff_pack_reviewed",
    "model_card_reviewed",
    "readiness_gate_reviewed",
    "risk_policy_boundary_reviewed",
    "rollback_plan_reviewed",
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


def _no_forbidden_true(*payloads: dict[str, Any]) -> bool:
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        for field in FORBIDDEN_TRUE_FIELDS:
            if _as_bool(payload.get(field)):
                return False
    return True


def build_paper_deployment_preflight_gate(
    handoff_pack: dict[str, Any],
    operator_checklist: dict[str, Any],
    runtime_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(handoff_pack, dict):
        raise ValueError("handoff_pack must be a dict")
    if not isinstance(operator_checklist, dict):
        raise ValueError("operator_checklist must be a dict")
    if runtime_context is None:
        runtime_context = {}
    if not isinstance(runtime_context, dict):
        raise ValueError("runtime_context must be a dict")

    missing_items = [item for item in REQUIRED_CHECKLIST_ITEMS if not _as_bool(operator_checklist.get(item))]

    checks = {
        "handoff_pack_ready": handoff_pack.get("paper_deployment_handoff_ready") is True,
        "handoff_pack_paper_only": handoff_pack.get("paper_only") is True,
        "operator_review_required": handoff_pack.get("operator_review_required") is True,
        "operator_checklist_complete": len(missing_items) == 0,
        "runtime_context_paper_only": runtime_context.get("paper_only", True) is True,
        "no_forbidden_real_action_flags": _no_forbidden_true(handoff_pack, operator_checklist, runtime_context),
    }

    blocked_reasons = [f"check_failed:{name}" for name, passed in checks.items() if not passed]
    preflight_passed = len(blocked_reasons) == 0

    return {
        "ok": True,
        "type": "paper_deployment_preflight_gate",
        "preflight_status": "passed" if preflight_passed else "blocked",
        "paper_preflight_passed": preflight_passed,
        "missing_checklist_items": missing_items,
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


def summarize_paper_deployment_preflight(preflight: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(preflight, dict):
        raise ValueError("preflight must be a dict")

    return {
        "ok": True,
        "type": "paper_deployment_preflight_summary",
        "status": preflight.get("preflight_status"),
        "paper_preflight_passed": preflight.get("paper_preflight_passed") is True,
        "blocked_reasons": preflight.get("blocked_reasons", []),
        "paper_only": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "operator_review_required": True,
    }
