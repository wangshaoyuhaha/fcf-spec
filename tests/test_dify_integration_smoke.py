from scripts.run_dify_integration_smoke import run_integration_smoke


def test_dify_integration_smoke_completes():
    result = run_integration_smoke()

    assert result["status"] == "completed"
    assert result["runner"] == "dify_adapter_response_integration_smoke"
    assert result["case_count"] == 3
    assert result["safe_boundary"]["no_real_exchange_api"] is True
    assert result["safe_boundary"]["no_real_order_placement"] is True
    assert result["safe_boundary"]["does_not_claim_real_trade_success"] is True


def test_dify_integration_smoke_cases_are_stable():
    result = run_integration_smoke()
    cases = {case["name"]: case for case in result["cases"]}

    success = cases["single_success_to_user_success"]
    assert success["adapter_http_status"] == 200
    assert success["adapter_ok"] is True
    assert success["user_response_type"] == "success"
    assert success["user_title"] == "市场输入处理完成"

    error = cases["single_bad_input_to_user_error"]
    assert error["adapter_http_status"] == 422
    assert error["adapter_ok"] is False
    assert error["user_response_type"] == "error"
    assert error["user_title"] == "市场输入校验失败"

    refusal = cases["forbidden_intent_to_safety_refusal"]
    assert refusal["adapter_http_status"] is None
    assert refusal["adapter_ok"] is None
    assert refusal["user_response_type"] == "safety_refusal"
    assert refusal["user_title"] == "已拒绝不安全操作"
