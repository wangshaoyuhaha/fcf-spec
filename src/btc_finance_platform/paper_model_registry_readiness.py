from typing import Any


SUPPORTED_ACTIONS = {
    "paper_deployment",
    "paper_parameter_update",
    "paper_registry_report",
}

REAL_ACTION_FLAGS = (
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
)


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "approved", "completed"}
    return bool(value)


def _operator_approved(model_card: dict[str, Any]) -> bool:
    approval = model_card.get("operator_approval")
    if isinstance(approval, dict):
        if _as_bool(approval.get("approved")):
            return True
        if _as_bool(approval.get("operator_approved")):
            return True

    return any(
        _as_bool(model_card.get(key))
        for key in (
            "operator_approved",
            "approved_by_operator",
            "model_card_approved",
        )
    )


def _paper_boundary_safe(payload: dict[str, Any]) -> bool:
    if payload.get("paper_only") is False:
        return False
    return not any(_as_bool(payload.get(flag)) for flag in REAL_ACTION_FLAGS)


def _registry_report_safe(registry_report: dict[str, Any] | None) -> bool:
    if registry_report is None:
        return True
    if not isinstance(registry_report, dict):
        return False
    if registry_report.get("paper_only") is False:
        return False
    blocked_flags = (
        "real_world_actions_allowed",
        "deployment_allowed_now",
        "parameter_update_allowed_now",
    )
    return not any(_as_bool(registry_report.get(flag)) for flag in blocked_flags)


def _blocked_reasons(checks: dict[str, bool]) -> list[str]:
    return [f"check_failed:{name}" for name, passed in checks.items() if not passed]


def evaluate_paper_model_registry_readiness(
    model_card: dict[str, Any],
    requested_action: str = "paper_deployment",
    registry_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(model_card, dict):
        raise ValueError("model_card must be a dict")

    model_id = str(
        model_card.get("model_id")
        or model_card.get("model_name")
        or model_card.get("name")
        or "unknown_model"
    ).strip()

    checks = {
        "model_card_present": bool(model_id),
        "requested_action_supported": requested_action in SUPPORTED_ACTIONS,
        "paper_only_boundary": _paper_boundary_safe(model_card),
        "operator_review_required": _as_bool(model_card.get("operator_review_required", True)),
        "operator_approval_recorded": _operator_approved(model_card),
        "bypass_operator_review_blocked": not _as_bool(model_card.get("bypass_operator_review")),
        "bypass_policy_risk_safe_boundary_blocked": not _as_bool(model_card.get("bypass_policy_risk_safe_boundary")),
        "registry_report_safe": _registry_report_safe(registry_report),
    }

    reasons = _blocked_reasons(checks)
    paper_action_allowed = len(reasons) == 0

    return {
        "ok": True,
        "type": "paper_model_registry_readiness_gate",
        "model_id": model_id,
        "requested_action": requested_action,
        "gate_status": "ready" if paper_action_allowed else "blocked",
        "paper_registry_action_allowed_now": paper_action_allowed,
        "paper_deployment_allowed_now": paper_action_allowed and requested_action == "paper_deployment",
        "paper_parameter_update_allowed_now": paper_action_allowed and requested_action == "paper_parameter_update",
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
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
        "operator_review_required": True,
        "checks": checks,
        "blocked_reasons": reasons,
    }


def build_paper_model_registry_readiness_report(
    model_cards: list[dict[str, Any]],
    registry_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(model_cards, list):
        raise ValueError("model_cards must be a list")
    if not model_cards:
        raise ValueError("model_cards must not be empty")

    results = [
        evaluate_paper_model_registry_readiness(
            model_card=card,
            requested_action="paper_deployment",
            registry_report=registry_report,
        )
        for card in model_cards
    ]
    ready_count = sum(1 for item in results if item["gate_status"] == "ready")
    blocked_count = len(results) - ready_count

    return {
        "ok": True,
        "type": "paper_model_registry_readiness_report",
        "report_status": "ready" if blocked_count == 0 else "blocked",
        "total_models": len(results),
        "ready_count": ready_count,
        "blocked_count": blocked_count,
        "results": results,
        "paper_only": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
        "operator_review_required": True,
    }
