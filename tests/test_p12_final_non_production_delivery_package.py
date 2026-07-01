from pathlib import Path

from fcf.api.dify_global_regression_api import handle_dify_global_regression_request
from fcf.api.operator_review_response_templates import render_operator_review_response
from fcf.regression.regression_stability_gate import evaluate_regression_stability_gate
from scripts.run_p10_dify_safe_package_summary import run_smoke as run_p10_package_summary
from scripts.run_p11_release_readiness_package_summary import run_smoke


DOC = Path("docs/111_p12_final_non_production_delivery_package.md")


def _text():
    return DOC.read_text(encoding="utf-8")


def test_p12_final_non_production_delivery_package_doc_exists():
    text = _text()

    assert DOC.exists()
    assert "P12-D2" in text
    assert "Final Non-production Delivery Package" in text


def test_p12_final_non_production_delivery_package_mentions_positioning():
    text = _text()

    for item in [
        "paper-only",
        "non-production",
        "operator handoff",
        "release readiness review",
        "regression stability review",
        "documentation hardening",
        "archive readiness",
        "final non-production delivery",
        "不是真实交易系统",
        "实盘下单系统",
        "真实成交系统",
        "真实资金管理系统",
        "真实交易信号系统",
        "自动实盘交易机器人",
        "production deployment package",
    ]:
        assert item in text


def test_p12_final_non_production_delivery_package_mentions_delivery_docs():
    text = _text()

    for item in [
        "README.md",
        "PROJECT_STATE.md",
        "docs/100_p11_release_readiness_plan.md",
        "docs/101_p11_operator_handoff_package.md",
        "docs/102_p11_versioned_run_commands.md",
        "docs/103_p11_artifact_inventory.md",
        "docs/104_p11_maintenance_checklist.md",
        "docs/105_p11_regression_stability_gate.md",
        "docs/106_p11_acceptance_smoke.md",
        "docs/107_p11_closeout_project_state.md",
        "docs/108_p11_post_closeout_release_readiness_package_summary.md",
        "docs/109_p11_to_p12_bridge_plan.md",
        "docs/110_p12_documentation_hardening_plan.md",
        "docs/111_p12_final_non_production_delivery_package.md",
    ]:
        assert item in text


def test_p12_final_non_production_delivery_package_mentions_final_commands():
    text = _text()

    for item in [
        "python main.py",
        "python scripts/run_all_smokes.py",
        "python scripts/run_p9_global_regression_summary.py",
        "python scripts/run_p10_dify_safe_package_summary.py",
        "python scripts/run_p11_acceptance_smoke.py",
        "python scripts/run_p11_release_readiness_package_summary.py",
        "python -m pytest -q",
        "events_recorded: 8",
        "status completed",
        "全部 passed",
    ]:
        assert item in text


def test_p12_final_non_production_delivery_package_mentions_dify_and_gate_entrypoints():
    text = _text()

    for item in [
        "fcf/api/dify_global_regression_api.py",
        "handle_dify_global_regression_request",
        "fcf/api/operator_review_response_templates.py",
        "render_operator_review_response",
        "fcf/regression/regression_stability_gate.py",
        "evaluate_regression_stability_gate",
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


def test_p12_final_non_production_delivery_package_mentions_pass_state_and_limits():
    text = _text()

    for item in [
        "只能说明",
        "paper-only regression 通过",
        "non-production 检查通过",
        "safe_boundary 当前 ok",
        "可以进入人工复核或归档准备",
        "不能说明",
        "真实交易信号成立",
        "真实下单成功",
        "真实成交成功",
        "真实资金发生变化",
        "真实账户余额已读取",
        "真实仓位已读取",
        "真实交易所已连接",
        "production deployment 已完成",
    ]:
        assert item in text


def test_p12_final_non_production_delivery_package_mentions_failed_rules_and_safety():
    text = _text()

    for item in [
        "立即停止",
        "不进入下一阶段",
        "不解释为交易信号",
        "不连接真实交易所",
        "不配置 API key",
        "不读取钱包私钥",
        "不尝试真实下单",
        "不删除测试绕过失败",
        "不修改 safe_boundary 绕过失败",
        "docs/94_p10_failure_triage_guide.md",
        "不接真实交易所 API",
        "不保存真实 API key",
        "不真实下单",
        "不读取真实账户余额",
        "不读取真实仓位",
        "不自动绕过人工复核",
        "不绕过 policy / risk / safe_boundary",
        "不把 paper-only passed 解释成真实交易信号",
        "不把 paper-only passed 解释成真实成交",
    ]:
        assert item in text


def test_p12_final_non_production_delivery_package_mentions_safe_boundary_fields_and_delivery_limits():
    text = _text()

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
        "non-production delivery package",
        "paper-only delivery package",
        "operator review package",
        "live trading package",
        "exchange execution package",
        "wallet custody package",
        "real-money trading package",
    ]:
        assert item in text


def test_p12_final_non_production_delivery_package_p11_summary_still_completed():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["package_summary"]["ready_for_p11_d10_bridge_plan"] is True
    assert result["package_summary"]["p11_acceptance_completed"] is True
    assert result["package_summary"]["regression_stability_gate_ok"] is True
    assert result["package_summary"]["safe_boundary_ok"] is True


def test_p12_final_non_production_delivery_package_adapter_template_and_gate_still_pass():
    api_response = handle_dify_global_regression_request(
        {
            "request_id": "p12-d2-final-delivery",
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
    gate_result = evaluate_regression_stability_gate(run_p10_package_summary())

    assert api_response["ok"] is True
    assert api_response["data"]["ready_for_operator_review"] is True
    assert user_response["response_type"] == "global_regression_passed"
    assert user_response["fields"]["real_execution"] is False
    assert gate_result["status"] == "completed"
    assert gate_result["ok"] is True
    assert gate_result["ready_for_p11_d7_acceptance_smoke"] is True


def test_p12_final_non_production_delivery_package_mentions_next_step():
    text = _text()

    assert "P12-D3" in text
    assert "archive readiness checklist" in text
