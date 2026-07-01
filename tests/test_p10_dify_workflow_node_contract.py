from pathlib import Path

from fcf.api.dify_global_regression_api import handle_dify_global_regression_request
from fcf.api.operator_review_response_templates import render_operator_review_response
from scripts.run_p9_global_regression_summary import run_smoke


DOC = Path("docs/95_p10_dify_workflow_node_contract.md")


def _doc_text():
    return DOC.read_text(encoding="utf-8")


def test_p10_dify_workflow_node_contract_doc_exists():
    text = _doc_text()

    assert DOC.exists()
    assert "P10-D6" in text
    assert "Dify Workflow Node Contract Document" in text


def test_p10_dify_workflow_node_contract_mentions_all_nodes():
    text = _doc_text()

    for node in [
        "Input validation node",
        "Global regression API node",
        "Safe boundary review node",
        "Operator response template node",
        "Human review node",
        "Final non-production output node",
    ]:
        assert node in text


def test_p10_dify_workflow_node_contract_mentions_entrypoints():
    text = _doc_text()

    for item in [
        "fcf/api/dify_global_regression_api.py",
        "handle_dify_global_regression_request",
        "fcf/api/operator_review_response_templates.py",
        "render_operator_review_response",
        "python scripts/run_all_smokes.py",
        "python scripts/run_p9_acceptance_smoke.py",
        "python scripts/run_p9_global_regression_summary.py",
        "python -m pytest -q",
    ]:
        assert item in text


def test_p10_dify_workflow_node_contract_mentions_input_contract():
    text = _doc_text()

    for item in [
        "request_id",
        "operator_id",
        "review_mode",
        "requested_checks",
        "output_format",
        "paper_only",
        "operator_review",
        "non_production_review",
        "all_smokes",
        "global_report",
        "safe_boundary",
        "project_state_consistency",
        "json",
    ]:
        assert item in text


def test_p10_dify_workflow_node_contract_mentions_rejected_inputs():
    text = _doc_text()

    for item in [
        "review_mode=live_trading",
        "requested_checks=real_exchange_balance",
        "output_format=html",
        "exchange_api_key",
        "wallet_private_key",
        "real_account_credentials",
        "real_broker_credentials",
        "live_order_request",
        "bypass_operator_review=true",
        "bypass_policy_risk_safe_boundary=true",
    ]:
        assert item in text


def test_p10_dify_workflow_node_contract_mentions_safe_boundary_rules():
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


def test_p10_dify_workflow_node_contract_mentions_response_types_and_human_review():
    text = _doc_text()

    for item in [
        "global_regression_passed",
        "global_regression_failed",
        "safe_boundary_failed",
        "project_state_inconsistent",
        "operator_review_required",
        "paper-only / non-production",
        "不是真实交易信号",
        "不是真实下单结果",
        "不是真实成交结果",
        "需要人工复核",
        "自动通过",
        "自动实盘交易",
        "绕过 safe_boundary",
        "绕过 policy / risk",
    ]:
        assert item in text


def test_p10_dify_workflow_node_contract_mentions_final_output_limits_and_safety():
    text = _doc_text()

    for item in [
        "paper-only regression status",
        "operator review required",
        "safe_boundary summary",
        "non-production notice",
        "next documentation step",
        "真实交易建议",
        "真实下单指令",
        "真实成交确认",
        "真实资金变化",
        "真实账户余额",
        "真实仓位",
        "交易所真实拒单",
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
    ]:
        assert item in text


def test_p10_dify_workflow_node_contract_current_global_summary_still_completed():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["global_summary"]["ready_for_phase10_planning"] is True
    assert result["global_summary"]["global_safe_boundary_ok"] is True
    assert result["global_summary"]["project_state_consistency_ok"] is True


def test_p10_dify_workflow_node_contract_adapter_and_template_still_pass():
    api_response = handle_dify_global_regression_request(
        {
            "request_id": "p10-d6-workflow",
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
    user_response = render_operator_review_response(api_response)

    assert api_response["ok"] is True
    assert api_response["data"]["ready_for_operator_review"] is True
    assert api_response["data"]["safe_boundary"]["real_execution"] is False
    assert api_response["data"]["safe_boundary"]["bypass_operator_review"] is False
    assert user_response["response_type"] == "global_regression_passed"
    assert user_response["fields"]["operator_review_required"] is True
    assert user_response["fields"]["bypass_policy_risk_safe_boundary"] is False
