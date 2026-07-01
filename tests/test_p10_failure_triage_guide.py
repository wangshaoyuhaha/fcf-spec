from copy import deepcopy
from pathlib import Path

from fcf.api.dify_global_regression_api import handle_dify_global_regression_request
from fcf.api.operator_review_response_templates import render_operator_review_response
from scripts.run_p9_global_regression_summary import run_smoke


DOC = Path("docs/94_p10_failure_triage_guide.md")


def _doc_text():
    return DOC.read_text(encoding="utf-8")


def _valid_api_response():
    return handle_dify_global_regression_request(
        {
            "request_id": "p10-d5-triage",
            "operator_id": "operator-paper-review",
            "review_mode": "operator_review",
            "requested_checks": [
                "all_smokes",
                "global_report",
                "safe_boundary",
                "project_state_consistency",
            ],
            "output_format": "json",
        }
    )


def test_p10_failure_triage_guide_doc_exists():
    text = _doc_text()

    assert DOC.exists()
    assert "P10-D5" in text
    assert "Failure Triage Guide" in text


def test_p10_failure_triage_guide_mentions_failure_categories():
    text = _doc_text()

    for item in [
        "pytest failed",
        "smoke failed",
        "safe_boundary failed",
        "project state consistency failed",
        "Dify adapter input invalid",
        "response template mismatch",
    ]:
        assert item in text


def test_p10_failure_triage_guide_mentions_commands_and_stop_rules():
    text = _doc_text()

    for item in [
        "python -m pytest -q",
        "python scripts/run_all_smokes.py",
        "python scripts/run_p9_acceptance_smoke.py",
        "python scripts/run_p9_global_regression_summary.py",
        "停止继续操作",
        "不要进入下一阶段",
        "不要把结果解释为交易信号",
        "不要连接真实交易所",
        "不要配置 API key",
        "不要读取钱包私钥",
        "不要尝试真实下单",
    ]:
        assert item in text


def test_p10_failure_triage_guide_mentions_safe_boundary_rules():
    text = _doc_text()

    for item in [
        "paper_only = true",
        "execution_mode = paper",
        "real_order = false",
        "real_execution = false",
        "real_exchange_api = false",
        "real_money_impact = false",
        "no_real_exchange_api = true",
        "no_real_order_placement = true",
        "no_exchange_api_key_storage = true",
        "no_wallet_private_key_access = true",
        "no_real_account_balance_read = true",
        "no_real_position_read = true",
        "does_not_claim_real_trade_success = true",
        "operator_review_required = true",
        "auto_live_trading = false",
        "bypass_operator_review = false",
        "bypass_policy_risk_safe_boundary = false",
    ]:
        assert item in text


def test_p10_failure_triage_guide_mentions_adapter_invalid_input_rules():
    text = _doc_text()

    for item in [
        "DifyGlobalRegressionSchemaError",
        "review_mode",
        "requested_checks",
        "output_format",
        "review_mode=live_trading",
        "real_exchange_balance",
        "output_format=html",
        "output_format=json",
        "operator_review",
        "paper_only",
        "non_production_review",
    ]:
        assert item in text


def test_p10_failure_triage_guide_mentions_response_template_rules():
    text = _doc_text()

    for item in [
        "render_operator_review_response",
        "global_regression_passed",
        "global_regression_failed",
        "safe_boundary_failed",
        "project_state_inconsistent",
        "operator_review_required",
        "fields.real_execution",
        "fields.real_exchange_api",
        "fields.operator_review_required",
        "fields.bypass_operator_review",
        "fields.bypass_policy_risk_safe_boundary",
    ]:
        assert item in text


def test_p10_failure_triage_guide_current_global_summary_still_completed():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["global_summary"]["ready_for_phase10_planning"] is True
    assert result["global_summary"]["global_safe_boundary_ok"] is True
    assert result["global_summary"]["project_state_consistency_ok"] is True


def test_p10_failure_triage_guide_adapter_invalid_input_maps_to_failed_response():
    api_response = handle_dify_global_regression_request(
        {
            "review_mode": "live_trading",
            "requested_checks": ["real_exchange_balance"],
            "output_format": "html",
        }
    )
    user_response = render_operator_review_response(api_response)

    assert api_response["ok"] is False
    assert api_response["error"]["type"] == "DifyGlobalRegressionSchemaError"
    assert user_response["response_type"] == "global_regression_failed"
    assert user_response["fields"]["real_execution"] is False
    assert user_response["fields"]["real_exchange_api"] is False


def test_p10_failure_triage_guide_safe_boundary_failure_maps_to_safe_boundary_failed():
    api_response = deepcopy(_valid_api_response())
    api_response["data"]["global_safe_boundary_check"]["status"] = "failed"
    api_response["data"]["global_safe_boundary_check"]["ok"] = False

    user_response = render_operator_review_response(api_response)

    assert user_response["response_type"] == "safe_boundary_failed"
    assert user_response["fields"]["real_execution"] is False
    assert user_response["fields"]["bypass_operator_review"] is False
    assert user_response["fields"]["bypass_policy_risk_safe_boundary"] is False


def test_p10_failure_triage_guide_mentions_safety_and_next_step():
    text = _doc_text()

    for item in [
        "不接真实交易所 API",
        "不保存真实 API key",
        "不读取钱包私钥",
        "不真实下单",
        "不读取真实账户余额",
        "不读取真实仓位",
        "不声明真实成交",
        "不声明真实资金影响",
        "不自动绕过人工复核",
        "不绕过 policy / risk / safe_boundary",
        "P10-D6",
        "Dify workflow node contract document",
    ]:
        assert item in text
