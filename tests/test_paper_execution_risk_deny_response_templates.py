from fcf.api.dify_paper_execution_adapter import (
    ROUTE_EXECUTE,
    route_dify_paper_execution_request,
)
from fcf.api.paper_execution_response_templates import (
    render_paper_execution_user_response,
    render_paper_risk_deny_response,
    render_paper_safety_refusal,
)


def _sample_paper_order():
    return {
        "asset_class": "Crypto",
        "symbol": "btcusdt",
        "venue": "BINANCE",
        "market_type": "PERP",
        "side": "BUY",
        "order_type": "LIMIT",
        "quantity": "0.25",
        "price": "60050.5",
        "time_in_force": "gtc",
        "source": "unit_test_risk_deny_templates",
        "correlation_id": "p6-d9-risk-deny-template",
        "metadata": {
            "note": "paper only",
        },
    }


def _safe_risk_context():
    return {
        "max_quantity": 1.0,
        "max_notional": 100000.0,
        "allow_leverage": False,
        "allow_margin": False,
        "duplicate_order_keys": [],
        "blocked_symbols": [],
        "blocked_asset_classes": [],
        "high_risk_flags": [],
    }


def _risk_deny_response():
    risk_context = _safe_risk_context()
    risk_context["max_quantity"] = 0.1

    return route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "raw_order": _sample_paper_order(),
            "simulation_mode": "simulated_fill",
            "risk_context": risk_context,
        },
    )


def _policy_deny_response():
    return route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "raw_order": _sample_paper_order(),
            "simulation_mode": "simulated_fill",
            "bypass_risk_requested": True,
            "risk_context": _safe_risk_context(),
        },
    )


def _value_error_response():
    raw_order = _sample_paper_order()
    raw_order["quantity"] = "-1"

    return route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "raw_order": raw_order,
            "simulation_mode": "simulated_fill",
            "risk_context": _safe_risk_context(),
        },
    )


def test_render_paper_risk_deny_response_is_stable_and_safe():
    adapter_response = _risk_deny_response()
    result = render_paper_risk_deny_response(adapter_response)

    assert adapter_response["http_status"] == 422
    assert adapter_response["body"]["error"]["type"] == "RiskDeny"

    assert result["ok"] is True
    assert result["api"] == "paper_execution_response_templates"
    assert result["response_type"] == "paper_risk_deny"
    assert result["title"] == "纸面模拟执行被风控规则拒绝"
    assert result["fields"]["error_type"] == "RiskDeny"
    assert "max_quantity" in result["fields"]["error_message"]
    assert result["fields"]["risk_denied"] is True
    assert result["fields"]["not_exchange_reject"] is True
    assert result["fields"]["real_order"] is False
    assert result["fields"]["real_execution"] is False
    assert result["fields"]["real_exchange_api"] is False
    assert result["fields"]["real_money_impact"] is False
    assert "不是交易所真实拒单" in result["message"]
    assert "没有真实下单" in result["message"]
    assert "没有真实下单" in result["safety_notice"]


def test_render_user_response_routes_risk_deny_to_risk_template():
    result = render_paper_execution_user_response(_risk_deny_response())

    assert result["response_type"] == "paper_risk_deny"
    assert result["title"] == "纸面模拟执行被风控规则拒绝"
    assert result["fields"]["error_type"] == "RiskDeny"
    assert result["fields"]["risk_denied"] is True
    assert result["fields"]["not_exchange_reject"] is True


def test_render_user_response_keeps_policy_deny_as_policy_template():
    result = render_paper_execution_user_response(_policy_deny_response())

    assert result["response_type"] == "paper_policy_deny"
    assert result["title"] == "纸面模拟执行被策略规则拒绝"
    assert result["fields"]["error_type"] == "PolicyDeny"
    assert result["fields"]["policy_denied"] is True


def test_render_user_response_keeps_value_error_as_execution_error():
    result = render_paper_execution_user_response(_value_error_response())

    assert result["response_type"] == "paper_execution_error"
    assert result["title"] == "纸面模拟执行校验失败"
    assert result["fields"]["error_type"] == "ValueError"
    assert "quantity" in result["fields"]["error_message"]


def test_safety_refusal_is_separate_from_risk_deny():
    result = render_paper_safety_refusal("real_execution")

    assert result["response_type"] == "paper_safety_refusal"
    assert result["title"] == "已拒绝不安全的真实执行请求"
    assert result["fields"]["intent"] == "real_execution"
    assert "不能真实下单" in result["message"]
