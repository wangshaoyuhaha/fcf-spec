from typing import Any, Dict


CHECKER_NAME = "global_safe_boundary_checker"
CHECKER_VERSION = "0.1.0"

REQUIRED_SAFE_BOUNDARY = {
    "paper_only": True,
    "execution_mode": "paper",
    "real_order": False,
    "real_execution": False,
    "real_exchange_api": False,
    "real_money_impact": False,
    "no_real_exchange_api": True,
    "no_real_order_placement": True,
    "no_exchange_api_key_storage": True,
    "no_wallet_private_key_access": True,
    "no_real_account_balance_read": True,
    "no_real_position_read": True,
    "does_not_claim_real_trade_success": True,
    "ci_secret_required": False,
    "production_deployment": False,
}


def _extract_safe_boundary(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        return {}

    nested = payload.get("safe_boundary")
    if isinstance(nested, dict):
        return nested

    return payload


def check_global_safe_boundary(payload: Dict[str, Any]) -> Dict[str, Any]:
    safe_boundary = _extract_safe_boundary(payload)

    checks = {}
    violations = []

    for key, expected in REQUIRED_SAFE_BOUNDARY.items():
        actual = safe_boundary.get(key)
        passed = actual == expected
        checks[key] = {
            "expected": expected,
            "actual": actual,
            "passed": passed,
        }
        if not passed:
            violations.append(
                {
                    "key": key,
                    "expected": expected,
                    "actual": actual,
                }
            )

    ok = len(violations) == 0

    return {
        "status": "completed" if ok else "failed",
        "checker": CHECKER_NAME,
        "checker_version": CHECKER_VERSION,
        "ok": ok,
        "checks": checks,
        "violations": violations,
        "safe_boundary": safe_boundary,
        "ready_for_p9_d5_project_state_checker": ok,
    }
