from fcf.api.dify_response_templates import (
    render_dify_user_response,
    render_error_response,
    render_safety_refusal,
    render_success_response,
)


def _success_fcf_response():
    return {
        "http_status": 200,
        "body": {
            "ok": True,
            "api": "local_market_input_api",
            "api_version": "0.1.0",
            "error": None,
            "data": {
                "status": "completed",
                "event_count": 1,
                "persisted": True,
                "output_path": "runtime/events/example.jsonl",
                "replay": {
                    "status": "completed",
                    "event_count": 1,
                },
            },
        },
    }


def _error_fcf_response():
    return {
        "http_status": 422,
        "body": {
            "ok": False,
            "api": "local_market_input_api",
            "api_version": "0.1.0",
            "error": {
                "type": "ValueError",
                "message": "last_price must be a valid number",
            },
            "data": None,
        },
    }


def test_render_success_response_is_stable_and_safe():
    result = render_success_response(_success_fcf_response())

    assert result["ok"] is True
    assert result["api"] == "dify_response_templates"
    assert result["response_type"] == "success"
    assert result["title"] == "市场输入处理完成"
    assert result["fields"]["event_count"] == 1
    assert result["fields"]["replay_status"] == "completed"
    assert result["fields"]["replay_event_count"] == 1
    assert result["fields"]["persisted"] is True
    assert "没有真实下单" in result["safety_notice"]


def test_render_error_response_is_stable_and_safe():
    result = render_error_response(_error_fcf_response())

    assert result["ok"] is True
    assert result["api"] == "dify_response_templates"
    assert result["response_type"] == "error"
    assert result["title"] == "市场输入校验失败"
    assert result["fields"]["error_type"] == "ValueError"
    assert "last_price" in result["fields"]["error_message"]
    assert "没有连接真实交易所" in result["safety_notice"]


def test_render_safety_refusal_blocks_real_trading_intent():
    result = render_safety_refusal("place_real_order")

    assert result["ok"] is True
    assert result["response_type"] == "safety_refusal"
    assert result["title"] == "已拒绝不安全操作"
    assert result["fields"]["intent"] == "place_real_order"
    assert "place_real_order" in result["fields"]["forbidden_intents"]
    assert "不能真实下单" in result["message"]


def test_render_dify_user_response_routes_success_error_and_refusal():
    success = render_dify_user_response(_success_fcf_response())
    error = render_dify_user_response(_error_fcf_response())
    refusal = render_dify_user_response(intent="connect_exchange")

    assert success["response_type"] == "success"
    assert error["response_type"] == "error"
    assert refusal["response_type"] == "safety_refusal"
