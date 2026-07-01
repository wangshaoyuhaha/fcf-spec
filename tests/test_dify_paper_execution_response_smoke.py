from scripts.run_dify_paper_execution_response_smoke import (
    run_dify_paper_execution_response_smoke,
)


def test_dify_paper_execution_response_smoke_completes_and_is_safe():
    result = run_dify_paper_execution_response_smoke()

    assert result["status"] == "completed"
    assert result["runner"] == "dify_paper_execution_response_smoke"
    assert result["case_count"] == 6
    assert result["safe_boundary"]["execution_mode"] == "paper"
    assert result["safe_boundary"]["real_order"] is False
    assert result["safe_boundary"]["real_execution"] is False
    assert result["safe_boundary"]["no_real_exchange_api"] is True
    assert result["safe_boundary"]["no_real_order_placement"] is True
    assert result["safe_boundary"]["does_not_claim_real_trade_success"] is True
    assert result["safe_boundary"]["does_not_claim_policy_deny_as_exchange_reject"] is True
    assert result["safe_boundary"]["does_not_claim_risk_deny_as_exchange_reject"] is True


def test_dify_paper_execution_response_smoke_success_cases_are_stable():
    result = run_dify_paper_execution_response_smoke()
    cases = {case["name"]: case for case in result["cases"]}

    fill = cases["fill_to_user_paper_fill_success"]
    assert fill["adapter_http_status"] == 200
    assert fill["adapter_ok"] is True
    assert fill["adapter_api"] == "paper_execution_api"
    assert fill["adapter_error_type"] is None
    assert fill["user_response_type"] == "paper_fill_success"
    assert fill["user_title"] == "纸面模拟成交完成"
    assert fill["user_safety_notice_present"] is True

    reject = cases["reject_to_user_paper_reject_success"]
    assert reject["adapter_http_status"] == 200
    assert reject["adapter_ok"] is True
    assert reject["adapter_api"] == "paper_execution_api"
    assert reject["adapter_error_type"] is None
    assert reject["user_response_type"] == "paper_reject_success"
    assert reject["user_title"] == "纸面模拟拒单完成"
    assert reject["user_safety_notice_present"] is True


def test_dify_paper_execution_response_smoke_policy_deny_case_is_stable():
    result = run_dify_paper_execution_response_smoke()
    cases = {case["name"]: case for case in result["cases"]}

    policy_deny = cases["policy_deny_to_user_paper_policy_deny"]
    assert policy_deny["adapter_http_status"] == 422
    assert policy_deny["adapter_ok"] is False
    assert policy_deny["adapter_api"] == "paper_execution_api"
    assert policy_deny["adapter_error_type"] == "PolicyDeny"
    assert policy_deny["user_response_type"] == "paper_policy_deny"
    assert policy_deny["user_title"] == "纸面模拟执行被策略规则拒绝"
    assert policy_deny["user_error_type"] == "PolicyDeny"
    assert policy_deny["policy_denied"] is True
    assert policy_deny["risk_denied"] is None
    assert policy_deny["not_exchange_reject"] is True
    assert policy_deny["user_safety_notice_present"] is True


def test_dify_paper_execution_response_smoke_risk_deny_case_is_stable():
    result = run_dify_paper_execution_response_smoke()
    cases = {case["name"]: case for case in result["cases"]}

    risk_deny = cases["risk_deny_to_user_paper_risk_deny"]
    assert risk_deny["adapter_http_status"] == 422
    assert risk_deny["adapter_ok"] is False
    assert risk_deny["adapter_api"] == "paper_execution_api"
    assert risk_deny["adapter_error_type"] == "RiskDeny"
    assert risk_deny["user_response_type"] == "paper_risk_deny"
    assert risk_deny["user_title"] == "纸面模拟执行被风控规则拒绝"
    assert risk_deny["user_error_type"] == "RiskDeny"
    assert risk_deny["policy_denied"] is None
    assert risk_deny["risk_denied"] is True
    assert risk_deny["not_exchange_reject"] is True
    assert risk_deny["user_safety_notice_present"] is True


def test_dify_paper_execution_response_smoke_error_case_is_stable():
    result = run_dify_paper_execution_response_smoke()
    cases = {case["name"]: case for case in result["cases"]}

    error = cases["bad_order_to_user_paper_execution_error"]
    assert error["adapter_http_status"] == 422
    assert error["adapter_ok"] is False
    assert error["adapter_api"] == "paper_execution_api"
    assert error["adapter_error_type"] == "ValueError"
    assert error["user_response_type"] == "paper_execution_error"
    assert error["user_title"] == "纸面模拟执行校验失败"
    assert error["user_error_type"] == "ValueError"
    assert error["policy_denied"] is None
    assert error["risk_denied"] is None
    assert error["user_safety_notice_present"] is True


def test_dify_paper_execution_response_smoke_safety_refusal_is_stable():
    result = run_dify_paper_execution_response_smoke()
    cases = {case["name"]: case for case in result["cases"]}

    refusal = cases["real_execution_intent_to_safety_refusal"]
    assert refusal["adapter_http_status"] is None
    assert refusal["adapter_ok"] is None
    assert refusal["adapter_api"] is None
    assert refusal["adapter_error_type"] is None
    assert refusal["user_response_type"] == "paper_safety_refusal"
    assert refusal["user_title"] == "已拒绝不安全的真实执行请求"
    assert refusal["user_safety_notice_present"] is True
