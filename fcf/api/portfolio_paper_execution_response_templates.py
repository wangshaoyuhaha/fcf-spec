from typing import Any, Dict


RESPONSE_TEMPLATE_NAME = "portfolio_paper_execution_response_templates"
RESPONSE_TEMPLATE_VERSION = "0.1.0"

SAFETY_NOTICE = (
    "这是 portfolio paper-only execution 响应：没有真实下单，没有连接真实交易所，"
    "没有保存真实 API key，没有读取钱包私钥，没有真实成交，没有真实资金影响。"
)


def _empty_fields() -> Dict[str, Any]:
    return {
        "portfolio_id": None,
        "portfolio_status": None,
        "execution_mode": "paper",
        "order_count": 0,
        "filled_count": 0,
        "sandbox_rejected_count": 0,
        "policy_denied_count": 0,
        "risk_denied_count": 0,
        "asset_class_counts": {},
        "branch_counts": {},
        "total_notional": 0,
        "notional_by_asset_class": {},
        "real_order": False,
        "real_execution": False,
        "real_exchange_api": False,
        "real_money_impact": False,
        "not_exchange_reject": True,
    }


def _fields_from_data(data: Dict[str, Any]) -> Dict[str, Any]:
    safe_boundary = data.get("safe_boundary") or {}
    fields = _empty_fields()
    fields.update(
        {
            "portfolio_id": data.get("portfolio_id"),
            "portfolio_status": data.get("portfolio_status"),
            "execution_mode": data.get("execution_mode", "paper"),
            "order_count": data.get("order_count", 0),
            "filled_count": data.get("filled_count", 0),
            "sandbox_rejected_count": data.get("sandbox_rejected_count", 0),
            "policy_denied_count": data.get("policy_denied_count", 0),
            "risk_denied_count": data.get("risk_denied_count", 0),
            "asset_class_counts": data.get("asset_class_counts") or {},
            "branch_counts": data.get("branch_counts") or {},
            "total_notional": data.get("total_notional", 0),
            "notional_by_asset_class": data.get("notional_by_asset_class") or {},
            "real_order": safe_boundary.get("real_order", False) is True,
            "real_execution": safe_boundary.get("real_execution", False) is True,
            "real_exchange_api": safe_boundary.get("real_exchange_api", False) is True,
            "real_money_impact": safe_boundary.get("real_money_impact", False) is True,
            "not_exchange_reject": True,
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
        "template": RESPONSE_TEMPLATE_NAME,
        "template_version": RESPONSE_TEMPLATE_VERSION,
        "title": title,
        "message": message,
        "fields": fields,
        "safety_notice": SAFETY_NOTICE,
    }


def render_portfolio_paper_execution_user_response(
    api_response: Dict[str, Any],
) -> Dict[str, Any]:
    if not isinstance(api_response, dict):
        return _base_response(
            response_type="portfolio_schema_error",
            title="Portfolio paper execution request invalid",
            message="Portfolio paper execution response is not a dict. 没有真实下单。",
            fields=_empty_fields(),
        )

    data = api_response.get("data") or {}
    error = api_response.get("error") or {}
    fields = _fields_from_data(data) if isinstance(data, dict) else _empty_fields()

    if api_response.get("ok") is True:
        if fields.get("portfolio_status") == "completed":
            return _base_response(
                response_type="portfolio_paper_success",
                title="Portfolio paper execution completed",
                message="Portfolio paper execution 已完成。该结果仅为 paper-only，没有真实下单，没有真实成交。",
                fields=fields,
            )

        return _base_response(
            response_type="portfolio_paper_partial_success",
            title="Portfolio paper execution partially completed",
            message="Portfolio paper execution 出现混合结果。sandbox reject 不是交易所真实拒单，没有真实下单。",
            fields=fields,
        )

    error_type = error.get("type")

    if error_type == "PortfolioPolicyDeny":
        fields["portfolio_policy_denied"] = True
        fields["portfolio_risk_denied"] = False
        fields["not_exchange_reject"] = True
        return _base_response(
            response_type="portfolio_policy_deny",
            title="Portfolio paper execution blocked by policy",
            message="Portfolio-level policy gate 已拒绝该 paper execution。这不是交易所真实拒单，也没有真实下单。",
            fields=fields,
        )

    if error_type == "PortfolioRiskDeny":
        fields["portfolio_policy_denied"] = False
        fields["portfolio_risk_denied"] = True
        fields["not_exchange_reject"] = True
        return _base_response(
            response_type="portfolio_risk_deny",
            title="Portfolio paper execution blocked by risk guardian",
            message="Portfolio-level risk guardian 已拒绝该 paper execution。这不是交易所真实拒单，也没有真实下单。",
            fields=fields,
        )

    fields["portfolio_schema_error"] = True
    fields["not_exchange_reject"] = True
    return _base_response(
        response_type="portfolio_schema_error",
        title="Portfolio paper execution schema error",
        message="Portfolio paper execution schema validation 失败。没有进入真实交易所，也没有真实下单。",
        fields=fields,
    )
