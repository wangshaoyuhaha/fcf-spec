from typing import Any, Dict, Iterable, List, Optional

from fcf.regression.global_regression_report_schema import build_global_regression_report
from fcf.regression.global_safe_boundary_checker import check_global_safe_boundary
from fcf.regression.project_state_consistency_checker import check_project_state_consistency
from scripts.run_all_smokes import run_all_smokes


API_NAME = "dify_global_regression_api"
API_VERSION = "0.1.0"

ALLOWED_REVIEW_MODES = {
    "paper_only",
    "operator_review",
    "non_production_review",
}

ALLOWED_OUTPUT_FORMATS = {
    "json",
}

ALLOWED_CHECKS = {
    "all_smokes",
    "global_report",
    "safe_boundary",
    "project_state_consistency",
}

DEFAULT_CHECKS = [
    "all_smokes",
    "global_report",
    "safe_boundary",
    "project_state_consistency",
]


def _safe_boundary() -> Dict[str, Any]:
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
        "operator_review_required": True,
        "auto_live_trading": False,
        "bypass_operator_review": False,
        "bypass_policy_risk_safe_boundary": False,
    }


def _response(
    *,
    ok: bool,
    error: Optional[Dict[str, Any]],
    data: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "ok": ok,
        "api": API_NAME,
        "api_version": API_VERSION,
        "error": error,
        "data": data,
    }


def _error(error_type: str, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "type": error_type,
        "message": message,
        "details": details or {},
    }


def _normalize_checks(value: Any) -> List[str]:
    if value is None:
        return list(DEFAULT_CHECKS)
    if isinstance(value, str):
        return [value]
    if isinstance(value, Iterable):
        return [str(item) for item in value]
    return []


def _validate_request(request: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(request, dict):
        return _error(
            "DifyGlobalRegressionSchemaError",
            "request must be a dict",
        )

    review_mode = request.get("review_mode", "operator_review")
    if review_mode not in ALLOWED_REVIEW_MODES:
        return _error(
            "DifyGlobalRegressionSchemaError",
            "unsupported review_mode",
            {
                "review_mode": review_mode,
                "allowed_review_modes": sorted(ALLOWED_REVIEW_MODES),
            },
        )

    output_format = request.get("output_format", "json")
    if output_format not in ALLOWED_OUTPUT_FORMATS:
        return _error(
            "DifyGlobalRegressionSchemaError",
            "unsupported output_format",
            {
                "output_format": output_format,
                "allowed_output_formats": sorted(ALLOWED_OUTPUT_FORMATS),
            },
        )

    requested_checks = _normalize_checks(request.get("requested_checks"))
    unknown_checks = sorted(set(requested_checks) - ALLOWED_CHECKS)
    if unknown_checks:
        return _error(
            "DifyGlobalRegressionSchemaError",
            "unsupported requested_checks",
            {
                "unknown_checks": unknown_checks,
                "allowed_checks": sorted(ALLOWED_CHECKS),
            },
        )

    return None


def handle_dify_global_regression_request(request: Dict[str, Any]) -> Dict[str, Any]:
    validation_error = _validate_request(request)
    if validation_error is not None:
        return _response(
            ok=False,
            error=validation_error,
            data={
                "safe_boundary": _safe_boundary(),
            },
        )

    requested_checks = _normalize_checks(request.get("requested_checks"))
    review_mode = request.get("review_mode", "operator_review")
    output_format = request.get("output_format", "json")

    all_smokes = run_all_smokes() if "all_smokes" in requested_checks else None
    report = (
        build_global_regression_report(all_smokes or {})
        if "global_report" in requested_checks
        else None
    )
    safe_boundary_check = (
        check_global_safe_boundary(report or {"safe_boundary": _safe_boundary()})
        if "safe_boundary" in requested_checks
        else None
    )
    project_state_check = (
        check_project_state_consistency()
        if "project_state_consistency" in requested_checks
        else None
    )

    checks_ok = [
        all_smokes is None or all_smokes.get("status") == "completed",
        report is None or report.get("status") == "completed",
        safe_boundary_check is None or safe_boundary_check.get("ok") is True,
        project_state_check is None or project_state_check.get("ok") is True,
    ]
    ok = all(checks_ok)

    safe_boundary = _safe_boundary()
    if isinstance(report, dict):
        safe_boundary.update(report.get("safe_boundary") or {})

    data = {
        "request_id": request.get("request_id"),
        "operator_id": request.get("operator_id"),
        "review_mode": review_mode,
        "requested_checks": requested_checks,
        "output_format": output_format,
        "run_all_smokes": all_smokes,
        "global_regression_report": report,
        "global_safe_boundary_check": safe_boundary_check,
        "project_state_consistency_check": project_state_check,
        "operator_review_required": True,
        "ready_for_operator_review": ok,
        "safe_boundary": safe_boundary,
    }

    return _response(
        ok=ok,
        error=None if ok else _error(
            "DifyGlobalRegressionCheckFailed",
            "one or more requested paper-only regression checks failed",
        ),
        data=data,
    )
