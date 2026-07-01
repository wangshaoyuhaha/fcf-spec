from typing import Any, Dict, Optional


REPORT_VERSION = "0.1.0"
GENERATED_BY = "global_regression_report_schema"


def _default_safe_boundary() -> Dict[str, Any]:
    return {
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


def _default_counts() -> Dict[str, int]:
    return {
        "total_smoke_count": 0,
        "completed_count": 0,
        "failed_count": 0,
        "ready_count": 0,
    }


def _default_readiness() -> Dict[str, Any]:
    return {
        "phase": "P9",
        "global_regression_suite_ready": False,
        "ready_for_p9_d3_report_schema": False,
        "ready_for_p9_d4_safe_boundary_checker": False,
    }


def _next_action(readiness: Dict[str, Any]) -> str:
    if readiness.get("global_regression_suite_ready") is True:
        return "P9-D4：global safe boundary checker"
    return "Fix failing smoke / regression suite before continuing"


def build_global_regression_report(
    suite_result: Dict[str, Any],
    *,
    report_path: Optional[str] = None,
) -> Dict[str, Any]:
    if not isinstance(suite_result, dict):
        suite_result = {}

    readiness = dict(_default_readiness())
    readiness.update(suite_result.get("readiness") or {})
    readiness["ready_for_p9_d4_safe_boundary_checker"] = (
        readiness.get("global_regression_suite_ready") is True
    )

    counts = dict(_default_counts())
    counts.update(suite_result.get("counts") or {})

    safe_boundary = dict(_default_safe_boundary())
    safe_boundary.update(suite_result.get("safe_boundary") or {})

    return {
        "report_version": REPORT_VERSION,
        "generated_by": GENERATED_BY,
        "phase": "P9",
        "status": suite_result.get("status", "failed"),
        "source_runner": suite_result.get("runner"),
        "suites": suite_result.get("suites") or [],
        "counts": counts,
        "readiness": readiness,
        "safe_boundary": safe_boundary,
        "report_path": report_path,
        "next_action": _next_action(readiness),
    }
