from typing import Any, Dict, List


GATE_NAME = "regression_stability_gate"
GATE_VERSION = "0.1.0"


def _check(name: str, actual: Any, expected: Any) -> Dict[str, Any]:
    return {
        "name": name,
        "actual": actual,
        "expected": expected,
        "passed": actual == expected,
    }


def _nested(payload: Dict[str, Any], *keys: str) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _violations(checks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "name": check["name"],
            "actual": check["actual"],
            "expected": check["expected"],
        }
        for check in checks
        if check["passed"] is not True
    ]


def evaluate_regression_stability_gate(package_result: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(package_result, dict):
        package_result = {}

    safe_boundary = package_result.get("safe_boundary")
    if not isinstance(safe_boundary, dict):
        safe_boundary = {}

    checks = [
        _check("package_status_completed", package_result.get("status"), "completed"),
        _check(
            "ready_for_p10_d10_bridge_plan",
            _nested(package_result, "package_summary", "ready_for_p10_d10_bridge_plan"),
            True,
        ),
        _check(
            "p10_acceptance_completed",
            _nested(package_result, "package_summary", "p10_acceptance_completed"),
            True,
        ),
        _check(
            "dify_global_regression_ok",
            _nested(package_result, "package_summary", "dify_global_regression_ok"),
            True,
        ),
        _check(
            "operator_response_passed",
            _nested(package_result, "package_summary", "operator_response_passed"),
            True,
        ),
        _check(
            "operator_review_required",
            _nested(package_result, "package_summary", "operator_review_required"),
            True,
        ),
        _check(
            "ready_for_operator_review",
            _nested(package_result, "package_summary", "ready_for_operator_review"),
            True,
        ),
        _check(
            "deliverables_all_present",
            _nested(package_result, "package_summary", "deliverables_all_present"),
            True,
        ),
        _check(
            "package_safe_boundary_ok",
            _nested(package_result, "package_summary", "safe_boundary_ok"),
            True,
        ),
        _check(
            "deliverables_all_present_field",
            _nested(package_result, "deliverables", "all_present"),
            True,
        ),
        _check(
            "deliverables_count_match",
            _nested(package_result, "deliverables", "present_count"),
            _nested(package_result, "deliverables", "deliverable_count"),
        ),
        _check(
            "dify_adapter_ok",
            _nested(package_result, "components", "dify_global_regression_adapter", "ok"),
            True,
        ),
        _check(
            "operator_response_type",
            _nested(package_result, "components", "operator_review_response", "response_type"),
            "global_regression_passed",
        ),
        _check("safe_boundary_paper_only", safe_boundary.get("paper_only"), True),
        _check("safe_boundary_real_order", safe_boundary.get("real_order"), False),
        _check("safe_boundary_real_execution", safe_boundary.get("real_execution"), False),
        _check("safe_boundary_real_exchange_api", safe_boundary.get("real_exchange_api"), False),
        _check("safe_boundary_real_money_impact", safe_boundary.get("real_money_impact"), False),
        _check("safe_boundary_operator_review_required", safe_boundary.get("operator_review_required"), True),
        _check("safe_boundary_auto_live_trading", safe_boundary.get("auto_live_trading"), False),
        _check("safe_boundary_bypass_operator_review", safe_boundary.get("bypass_operator_review"), False),
        _check(
            "safe_boundary_bypass_policy_risk_safe_boundary",
            safe_boundary.get("bypass_policy_risk_safe_boundary"),
            False,
        ),
    ]

    violations = _violations(checks)
    ok = len(violations) == 0

    return {
        "status": "completed" if ok else "failed",
        "gate": GATE_NAME,
        "gate_version": GATE_VERSION,
        "ok": ok,
        "checks": checks,
        "violations": violations,
        "ready_for_p11_d7_acceptance_smoke": ok,
        "safe_boundary": safe_boundary,
    }
