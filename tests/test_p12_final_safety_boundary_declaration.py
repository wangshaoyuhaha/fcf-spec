from pathlib import Path

from fcf.api.dify_global_regression_api import handle_dify_global_regression_request
from fcf.api.operator_review_response_templates import render_operator_review_response
from scripts.run_p11_release_readiness_package_summary import run_smoke


DOC = Path("docs/115_p12_final_safety_boundary_declaration.md")


def _text():
    return DOC.read_text(encoding="utf-8")


def test_p12_final_safety_boundary_declaration_doc_exists():
    text = _text()

    assert DOC.exists()
    assert "P12-D6" in text
    assert "Final Safety Boundary Declaration" in text


def test_p12_final_safety_boundary_declaration_mentions_version_and_scope():
    text = _text()

    for item in [
        "final_safety_boundary_declaration_version = 0.1.0",
        "declaration_mode = non_production",
        "paper_only = true",
        "phase = P12",
        "day = P12-D6",
        "status = active",
        "final non-production delivery",
        "archive readiness review",
        "operator handoff review",
        "release readiness review",
        "regression stability review",
        "safety boundary review",
    ]:
        assert item in text


def test_p12_final_safety_boundary_declaration_mentions_system_positioning():
    text = _text()

    for item in [
        "paper-only system",
        "non-production package",
        "multi-asset event system",
        "Dify-safe operator review package",
        "regression-first validation package",
        "release readiness package",
        "operator handoff package",
        "archive readiness package",
        "不是真实交易系统",
        "不是实盘下单系统",
        "不是真实成交系统",
        "不是真实资金管理系统",
        "不是真实交易信号系统",
        "不是自动实盘交易机器人",
        "不是 production deployment package",
        "不是 exchange execution package",
        "不是 wallet custody package",
        "不是 real-money trading package",
    ]:
        assert item in text


def test_p12_final_safety_boundary_declaration_mentions_prohibited_actions():
    text = _text()

    for item in [
        "禁止接真实交易所 API",
        "禁止保存真实 API key",
        "禁止读取钱包私钥",
        "禁止真实下单",
        "禁止读取真实账户余额",
        "禁止读取真实仓位",
        "禁止声明真实成交",
        "禁止声明真实资金影响",
        "禁止配置 CI secret",
        "禁止做 production deployment",
        "禁止自动实盘交易",
        "禁止自动绕过人工复核",
        "禁止绕过 policy / risk / safe_boundary",
        "禁止把 paper-only passed 解释成真实交易信号",
        "禁止把 paper-only passed 解释成真实成交",
    ]:
        assert item in text


def test_p12_final_safety_boundary_declaration_mentions_field_contract():
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
    ]:
        assert item in text


def test_p12_final_safety_boundary_declaration_mentions_allowed_and_disallowed_outputs():
    text = _text()

    for item in [
        "paper-only regression passed",
        "non-production validation passed",
        "safe_boundary ok",
        "operator review required",
        "ready_for_operator_review true",
        "ready_for_p11_d10_bridge_plan true",
        "archive readiness review can proceed",
        "final non-production delivery package can proceed",
        "real trade signal passed",
        "real order placed",
        "real fill completed",
        "real money impact confirmed",
        "real account balance read",
        "real position read",
        "real exchange connected",
        "production deployment completed",
        "auto live trading enabled",
        "operator review bypassed",
        "policy / risk / safe_boundary bypassed",
    ]:
        assert item in text


def test_p12_final_safety_boundary_declaration_mentions_failed_stop_rules():
    text = _text()

    for item in [
        "立即停止",
        "不进入下一阶段",
        "不进入归档状态",
        "不解释为交易信号",
        "不连接真实交易所",
        "不配置 API key",
        "不读取钱包私钥",
        "不尝试真实下单",
        "不删除测试绕过失败",
        "不修改 safe_boundary 绕过失败",
        "不绕过人工复核",
        "不绕过 policy / risk / safe_boundary",
        "保留完整错误输出",
        "docs/94_p10_failure_triage_guide.md",
    ]:
        assert item in text


def test_p12_final_safety_boundary_declaration_mentions_review_and_archive_requirements():
    text = _text()

    for item in [
        "operator_review_required = true",
        "ready_for_operator_review = true",
        "bypass_operator_review = false",
        "bypass_policy_risk_safe_boundary = false",
        "人工复核不能被自动跳过",
        "policy / risk / safe_boundary 不能被自动跳过",
        "docs/111_p12_final_non_production_delivery_package.md exists",
        "docs/112_p12_archive_readiness_checklist.md exists",
        "docs/113_p12_final_command_index.md exists",
        "docs/114_p12_final_artifact_manifest.md exists",
        "docs/115_p12_final_safety_boundary_declaration.md exists",
        "python scripts/run_p11_release_readiness_package_summary.py status completed",
        "ready_for_p11_d10_bridge_plan true",
        "python -m pytest -q 全部 passed",
        "git status --short 干净",
        "commit 已完成",
        "push 已完成",
    ]:
        assert item in text


def test_p12_final_safety_boundary_declaration_mentions_plain_language_declaration():
    text = _text()

    for item in [
        "FCF 当前交付包是 paper-only / non-production delivery package",
        "本地回归",
        "Dify-safe operator review",
        "release readiness review",
        "archive readiness review",
        "人工复核",
        "不能用于真实交易",
        "真实下单",
        "真实账户读取",
        "真实仓位读取",
        "钱包私钥读取",
        "真实资金管理",
        "production deployment",
        "自动实盘交易",
        "只能说明 paper-only / non-production regression passed",
        "不能说明真实交易信号成立",
        "不能说明真实下单成功",
        "不能说明真实成交成功",
        "不能说明真实资金发生变化",
    ]:
        assert item in text


def test_p12_final_safety_boundary_declaration_p11_summary_still_ready():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["package_summary"]["ready_for_p11_d10_bridge_plan"] is True
    assert result["package_summary"]["p11_acceptance_completed"] is True
    assert result["package_summary"]["regression_stability_gate_ok"] is True
    assert result["package_summary"]["deliverables_all_present"] is True
    assert result["package_summary"]["safe_boundary_ok"] is True


def test_p12_final_safety_boundary_declaration_adapter_template_boundary_still_pass():
    api_response = handle_dify_global_regression_request(
        {
            "request_id": "p12-d6-final-safety-boundary",
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
    boundary = api_response["data"]["safe_boundary"]

    assert api_response["ok"] is True
    assert api_response["data"]["operator_review_required"] is True
    assert api_response["data"]["ready_for_operator_review"] is True
    assert user_response["response_type"] == "global_regression_passed"
    assert boundary["paper_only"] is True
    assert boundary["real_order"] is False
    assert boundary["real_execution"] is False
    assert boundary["real_exchange_api"] is False
    assert boundary["real_money_impact"] is False
    assert boundary["auto_live_trading"] is False
    assert boundary["bypass_operator_review"] is False
    assert boundary["bypass_policy_risk_safe_boundary"] is False


def test_p12_final_safety_boundary_declaration_mentions_next_step():
    text = _text()

    assert "P12-D7" in text
    assert "final operator delivery note and Phase 12 acceptance smoke" in text
