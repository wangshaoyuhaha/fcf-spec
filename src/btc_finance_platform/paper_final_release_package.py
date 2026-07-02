from typing import Any


REQUIRED_RELEASE_SECTIONS = (
    "project_state_summary",
    "p10_model_registry_closeout",
    "p11_paper_deployment_closeout",
    "validation_summary",
    "paper_only_safety_boundary",
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


def build_paper_final_release_package(
    p10_closeout: dict[str, Any],
    p11_closeout: dict[str, Any],
    validation: dict[str, Any],
    sections: list[str],
) -> dict[str, Any]:
    if not isinstance(p10_closeout, dict):
        raise ValueError("p10_closeout must be a dict")
    if not isinstance(p11_closeout, dict):
        raise ValueError("p11_closeout must be a dict")
    if not isinstance(validation, dict):
        raise ValueError("validation must be a dict")
    if not isinstance(sections, list):
        raise ValueError("sections must be a list")

    missing_sections = [section for section in REQUIRED_RELEASE_SECTIONS if section not in sections]

    checks = {
        "p10_completed": p10_closeout.get("p10_completed") is True,
        "p11_completed": p11_closeout.get("p11_completed") is True,
        "validation_passed": validation.get("all_checks_passed") is True and validation.get("pytest_passed") is True,
        "release_sections_complete": len(missing_sections) == 0,
        "all_inputs_paper_only": all(item.get("paper_only") is True for item in (p10_closeout, p11_closeout, validation)),
        "operator_review_required": all(item.get("operator_review_required") is True for item in (p10_closeout, p11_closeout, validation)),
        "no_forbidden_real_action_flags": _no_forbidden_true(p10_closeout, p11_closeout, validation),
    }

    blocked_reasons = [f"check_failed:{name}" for name, passed in checks.items() if not passed]
    ready = len(blocked_reasons) == 0

    return {
        "ok": True,
        "type": "paper_final_release_package",
        "release_status": "ready" if ready else "blocked",
        "paper_final_release_ready": ready,
        "required_sections": list(REQUIRED_RELEASE_SECTIONS),
        "provided_sections": sections,
        "missing_sections": missing_sections,
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


def summarize_paper_final_release_package(package: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(package, dict):
        raise ValueError("package must be a dict")

    return {
        "ok": True,
        "type": "paper_final_release_package_summary",
        "status": package.get("release_status"),
        "paper_final_release_ready": package.get("paper_final_release_ready") is True,
        "missing_sections": package.get("missing_sections", []),
        "blocked_reasons": package.get("blocked_reasons", []),
        "paper_only": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "real_execution": False,
        "operator_review_required": True,
    }
