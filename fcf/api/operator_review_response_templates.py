from typing import Any, Dict


TEMPLATE_NAME = "operator_review_response_templates"
TEMPLATE_VERSION = "0.1.0"

SAFETY_NOTICE = (
    "这是 paper-only / non-production operator review 响应：不是真实交易信号，"
    "不是真实下单结果，不是真实成交结果，没有真实资金影响，需要人工复核。"
)


def _empty_fields() -> Dict[str, Any]:
    return {
        "request_id": None,
        "operator_id": None,
        "review_mode": None,
        "requested_checks": [],
        "output_format": None,
        "operator_review_required": True,
        "ready_for_operator_review": False,
        "paper_only": True,
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
        "auto_live_trading": False,
        "bypass_operator_review": False,
        "bypass_policy_risk_safe_boundary": False,
    }


def _fields_from_data(data: Dict[str, Any]) -> Dict[str, Any]:
    fields = _empty_fields()
    safe_boundary = data.get("safe_boundary") or {}

    fields.update(
        {
            "request_id": data.get("request_id"),
            "operator_id": data.get("operator_id"),
            "review_mode": data.get("review_mode"),
            "requested_checks": data.get("requested_checks") or [],
            "output_format": data.get("output_format"),
            "operator_review_required": data.get("operator_review_required", True) is True,
            "ready_for_operator_review": data.get("ready_for_operator_review", False) is True,
            "paper_only": safe_boundary.get("paper_only", True) is True,
            "real_order": safe_boundary.get("real_order", False) is True,
            "real_execution": safe_boundary.get("real_execution", False) is True,
            "real_exchange_api": safe_boundary.get("real_exchange_api", False) is True,
            "real_money_impact": safe_boundary.get("real_money_impact", False) is True,
            "no_real_exchange_api": safe_boundary.get("no_real_exchange_api", True) is True,
            "no_real_order_placement": safe_boundary.get("no_real_order_placement", True) is True,
            "no_exchange_api_key_storage": safe_boundary.get("no_exchange_api_key_storage", True) is True,
            "no_wallet_private_key_access": safe_boundary.get("no_wallet_private_key_access", True) is True,
            "no_real_account_balance_read": safe_boundary.get("no_real_account_balance_read", True) is True,
            "no_real_position_read": safe_boundary.get("no_real_position_read", True) is True,
            "does_not_claim_real_trade_success": safe_boundary.get("does_not_claim_real_trade_success", True) is True,
            "ci_secret_required": safe_boundary.get("ci_secret_required", False) is True,
            "production_deployment": safe_boundary.get("production_deployment", False) is True,
            "auto_live_trading": safe_boundary.get("auto_live_trading", False) is True,
            "bypass_operator_review": safe_boundary.get("bypass_operator_review", False) is True,
            "bypass_policy_risk_safe_boundary": safe_boundary.get("bypass_policy_risk_safe_boundary", False) is True,
        }
    )

    return fields


def _base_response(
    *,
    response_type: str,
    title: str,
    message: str,
    fields: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "response_type": response_type,
        "template": TEMPLATE_NAME,
        "template_version": TEMPLATE_VERSION,
        "title": title,
        "message": message,
        "fields": fields,
        "safety_notice": SAFETY_NOTICE,
    }


def _component(data: Dict[str, Any], key: str) -> Dict[str, Any]:
    value = data.get(key)
    return value if isinstance(value, dict) else {}


def _safe_boundary_failed(data: Dict[str, Any]) -> bool:
    check = _component(data, "global_safe_boundary_check")
    return check.get("ok") is False or check.get("status") == "failed"


def _project_state_inconsistent(data: Dict[str, Any]) -> bool:
    check = _component(data, "project_state_consistency_check")
    return check.get("ok") is False or check.get("status") == "failed"


def _global_regression_failed(data: Dict[str, Any]) -> bool:
    all_smokes = _component(data, "run_all_smokes")
    report = _component(data, "global_regression_report")
    return all_smokes.get("status") == "failed" or report.get("status") == "failed"


def render_operator_review_response(api_response: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(api_response, dict):
        return _base_response(
            response_type="operator_review_required",
            title="Operator review required",
            message=(
                "Dify global regression response 无效，需要人工复核。"
                "这是 paper-only / non-production 响应，不是真实交易信号。"
            ),
            fields=_empty_fields(),
        )

    data = api_response.get("data") or {}
    if not isinstance(data, dict):
        data = {}

    fields = _fields_from_data(data)

    if _safe_boundary_failed(data):
        return _base_response(
            response_type="safe_boundary_failed",
            title="Safe boundary check failed",
            message=(
                "global safe_boundary 检查失败，必须停止并人工复核。"
                "这不是真实下单结果，也不是真实成交结果。"
            ),
            fields=fields,
        )

    if _project_state_inconsistent(data):
        return _base_response(
            response_type="project_state_inconsistent",
            title="Project state consistency failed",
            message=(
                "PROJECT_STATE / README consistency 检查失败，需要人工复核。"
                "这是 paper-only / non-production 响应。"
            ),
            fields=fields,
        )

    if _global_regression_failed(data) or api_response.get("ok") is False:
        return _base_response(
            response_type="global_regression_failed",
            title="Global paper regression failed",
            message=(
                "global paper-only regression 未通过，需要人工复核。"
                "这不是真实交易信号，不是真实下单结果。"
            ),
            fields=fields,
        )

    required_checks = set(fields.get("requested_checks") or [])
    full_checks = {
        "all_smokes",
        "global_report",
        "safe_boundary",
        "project_state_consistency",
    }

    if required_checks != full_checks or fields["operator_review_required"] is True:
        if fields["ready_for_operator_review"] is True and required_checks == full_checks:
            return _base_response(
                response_type="global_regression_passed",
                title="Global paper regression passed",
                message=(
                    "global paper-only regression 已通过，可以进入人工复核。"
                    "这不是真实交易信号，不是真实下单结果，不是真实成交结果。"
                ),
                fields=fields,
            )

        return _base_response(
            response_type="operator_review_required",
            title="Operator review required",
            message=(
                "当前结果需要人工复核后才能继续。"
                "这是 paper-only / non-production 响应，不是真实交易信号。"
            ),
            fields=fields,
        )

    return _base_response(
        response_type="global_regression_passed",
        title="Global paper regression passed",
        message=(
            "global paper-only regression 已通过，可以进入人工复核。"
            "这不是真实交易信号，不是真实下单结果，不是真实成交结果。"
        ),
        fields=fields,
    )
