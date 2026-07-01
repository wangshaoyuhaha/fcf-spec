from pathlib import Path

from fcf.api.dify_global_regression_api import handle_dify_global_regression_request
from fcf.api.operator_review_response_templates import render_operator_review_response
from scripts.run_p9_global_regression_summary import run_smoke


DOC = Path("docs/93_p10_paper_only_operator_runbook.md")


def _doc_text():
    return DOC.read_text(encoding="utf-8")


def test_p10_paper_only_operator_runbook_doc_exists():
    text = _doc_text()

    assert DOC.exists()
    assert "P10-D4" in text
    assert "Paper-only Operator Runbook" in text


def test_p10_paper_only_operator_runbook_mentions_local_commands():
    text = _doc_text()

    for command in [
        "python main.py",
        "python scripts/run_all_smokes.py",
        "python scripts/run_p9_acceptance_smoke.py",
        "python scripts/run_p9_global_regression_summary.py",
        "python -m pytest -q",
    ]:
        assert command in text


def test_p10_paper_only_operator_runbook_mentions_adapter_and_template():
    text = _doc_text()

    for item in [
        "fcf/api/dify_global_regression_api.py",
        "handle_dify_global_regression_request",
        "fcf/api/operator_review_response_templates.py",
        "render_operator_review_response",
    ]:
        assert item in text


def test_p10_paper_only_operator_runbook_mentions_status_rules():
    text = _doc_text()

    for item in [
        "status completed",
        "ok true",
        "ready_for_operator_review true",
        "safe_boundary ok true",
        "只能说明",
        "不能说明",
        "真实交易信号成立",
        "真实下单成功",
        "真实成交成功",
        "真实资金发生变化",
    ]:
        assert item in text


def test_p10_paper_only_operator_runbook_mentions_safe_boundary_rules():
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


def test_p10_paper_only_operator_runbook_mentions_failed_handling_and_safety():
    text = _doc_text()

    for item in [
        "停止继续操作",
        "不要进入下一阶段",
        "不要把结果解释为交易信号",
        "不要连接真实交易所",
        "不要配置 API key",
        "不要读取钱包私钥",
        "不要尝试真实下单",
        "failure triage guide",
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


def test_p10_paper_only_operator_runbook_current_global_summary_still_completed():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["global_summary"]["ready_for_phase10_planning"] is True
    assert result["global_summary"]["global_safe_boundary_ok"] is True
    assert result["global_summary"]["project_state_consistency_ok"] is True


def test_p10_paper_only_operator_runbook_adapter_and_template_still_pass():
    api_response = handle_dify_global_regression_request(
        {
            "request_id": "p10-d4-runbook",
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
    assert user_response["response_type"] == "global_regression_passed"
    assert user_response["fields"]["operator_review_required"] is True
    assert user_response["fields"]["ready_for_operator_review"] is True
    assert user_response["fields"]["real_execution"] is False
    assert user_response["fields"]["bypass_operator_review"] is False
