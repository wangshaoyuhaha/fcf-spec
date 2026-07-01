from fcf.api.dify_paper_execution_adapter import (
    ROUTE_EXECUTE,
    route_dify_paper_execution_request,
)
from fcf.api.paper_execution_response_templates import (
    render_paper_execution_error_response,
    render_paper_execution_user_response,
    render_paper_fill_success_response,
    render_paper_reject_success_response,
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
        "source": "unit_test_paper_execution_templates",
        "correlation_id": "p5-d9-paper-execution-template",
        "metadata": {
            "note": "paper only",
        },
    }


def _fill_response():
    return route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "raw_order": _sample_paper_order(),
            "simulation_mode": "simulated_fill",
        },
    )


def _partial_fill_response():
    return route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "raw_order": _sample_paper_order(),
            "simulation_mode": "simulated_fill",
            "filled_quantity": "0.10",
            "fill_price": "60051.0",
        },
    )


def _reject_response():
    return route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "raw_order": _sample_paper_order(),
            "simulation_mode": "simulated_reject",
            "reject_reason": "policy denied in template test",
        },
    )


def _error_response():
    raw_order = _sample_paper_order()
    raw_order["quantity"] = "-1"
    return route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "raw_order": raw_order,
            "simulation_mode": "simulated_fill",
        },
    )


def test_render_paper_fill_success_response_is_stable_and_safe():
    result = render_paper_fill_success_response(_fill_response())

    assert result["ok"] is True
    assert result["api"] == "paper_execution_response_templates"
    assert result["response_type"] == "paper_fill_success"
    assert result["title"] == "纸面模拟成交完成"
    assert result["fields"]["execution_status"] == "filled"
    assert result["fields"]["event_name"] == "fcf.sandbox.execution.filled"
    assert result["fields"]["event_count"] == 1
    assert result["fields"]["replay_status"] == "completed"
    assert result["fields"]["symbol"] == "BTCUSDT"
    assert result["fields"]["real_order"] is False
    assert result["fields"]["real_execution"] is False
    assert "没有真实下单" in result["safety_notice"]


def test_render_paper_partial_fill_success_response_is_stable_and_safe():
    result = render_paper_execution_user_response(_partial_fill_response())

    assert result["response_type"] == "paper_fill_success"
    assert result["title"] == "纸面模拟部分成交完成"
    assert result["fields"]["execution_status"] == "partial_filled"
    assert result["fields"]["filled_quantity"] == 0.10
    assert result["fields"]["remaining_quantity"] == 0.15
    assert result["fields"]["fill_price"] == 60051.0
    assert result["fields"]["real_execution"] is False


def test_render_paper_reject_success_response_is_stable_and_safe():
    result = render_paper_reject_success_response(_reject_response())

    assert result["ok"] is True
    assert result["response_type"] == "paper_reject_success"
    assert result["title"] == "纸面模拟拒单完成"
    assert result["fields"]["execution_status"] == "rejected"
    assert result["fields"]["event_name"] == "fcf.sandbox.execution.rejected"
    assert result["fields"]["reject_reason"] == "policy denied in template test"
    assert result["fields"]["real_order"] is False
    assert result["fields"]["real_execution"] is False
    assert "不是交易所真实拒单" in result["message"]


def test_render_paper_execution_error_response_is_stable_and_safe():
    result = render_paper_execution_error_response(_error_response())

    assert result["ok"] is True
    assert result["response_type"] == "paper_execution_error"
    assert result["title"] == "纸面模拟执行校验失败"
    assert result["fields"]["error_type"] == "ValueError"
    assert "quantity" in result["fields"]["error_message"]
    assert "没有真实下单" in result["safety_notice"]


def test_render_paper_safety_refusal_blocks_real_execution_intent():
    result = render_paper_safety_refusal("place_real_order")

    assert result["ok"] is True
    assert result["response_type"] == "paper_safety_refusal"
    assert result["title"] == "已拒绝不安全的真实执行请求"
    assert result["fields"]["intent"] == "place_real_order"
    assert "place_real_order" in result["fields"]["forbidden_intents"]
    assert "不能真实下单" in result["message"]


def test_render_paper_execution_user_response_routes_all_branches():
    fill = render_paper_execution_user_response(_fill_response())
    reject = render_paper_execution_user_response(_reject_response())
    error = render_paper_execution_user_response(_error_response())
    refusal = render_paper_execution_user_response(intent="real_execution")
    missing = render_paper_execution_user_response()

    assert fill["response_type"] == "paper_fill_success"
    assert reject["response_type"] == "paper_reject_success"
    assert error["response_type"] == "paper_execution_error"
    assert refusal["response_type"] == "paper_safety_refusal"
    assert missing["response_type"] == "paper_execution_error"
    assert missing["fields"]["error_type"] == "MissingResponse"
