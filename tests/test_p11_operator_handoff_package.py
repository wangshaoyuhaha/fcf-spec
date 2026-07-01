from pathlib import Path

from fcf.api.dify_global_regression_api import handle_dify_global_regression_request
from fcf.api.operator_review_response_templates import render_operator_review_response
from scripts.run_p10_dify_safe_package_summary import run_smoke


DOC = Path("docs/101_p11_operator_handoff_package.md")


def _text():
    return DOC.read_text(encoding="utf-8")


def test_p11_operator_handoff_package_doc_exists():
    text = _text()

    assert DOC.exists()
    assert "P11-D2" in text
    assert "Operator Handoff Package" in text


def test_p11_operator_handoff_package_mentions_operator_scope():
    text = _text()

    for item in [
        "运行本地回归命令",
        "读取 smoke / regression status",
        "读取 safe_boundary",
        "调用 Dify-safe adapter",
        "阅读 operator review response",
        "识别 failed",
        "停止错误流程",
        "维护 README.md / PROJECT_STATE.md 一致性",
    ]:
        assert item in text


def test_p11_operator_handoff_package_mentions_system_positioning():
    text = _text()

    for item in [
        "paper-only",
        "non-production",
        "multi-asset event system",
        "Dify-safe operator review package",
        "regression-first validation package",
        "不是真实交易系统",
        "实盘下单系统",
        "真实成交系统",
        "真实资金管理系统",
        "自动实盘交易机器人",
    ]:
        assert item in text


def test_p11_operator_handoff_package_mentions_required_commands():
    text = _text()

    for command in [
        "python main.py",
        "python scripts/run_all_smokes.py",
        "python scripts/run_p9_global_regression_summary.py",
        "python scripts/run_p10_acceptance_smoke.py",
        "python scripts/run_p10_dify_safe_package_summary.py",
        "python -m pytest -q",
        "events_recorded: 8",
        "status completed",
    ]:
        assert command in text


def test_p11_operator_handoff_package_mentions_dify_entrypoints_and_response_types():
    text = _text()

    for item in [
        "fcf/api/dify_global_regression_api.py",
        "handle_dify_global_regression_request",
        "fcf/api/operator_review_response_templates.py",
        "render_operator_review_response",
        "paper_only",
        "operator_review",
        "non_production_review",
        "all_smokes",
        "global_report",
        "safe_boundary",
        "project_state_consistency",
        "global_regression_passed",
        "global_regression_failed",
        "safe_boundary_failed",
        "project_state_inconsistent",
        "operator_review_required",
    ]:
        assert item in text


def test_p11_operator_handoff_package_mentions_handoff_checklist_and_failed_rules():
    text = _text()

    for item in [
        "README.md 存在",
        "PROJECT_STATE.md 存在",
        "docs/100_p11_release_readiness_plan.md 存在",
        "docs/101_p11_operator_handoff_package.md 存在",
        "scripts/run_all_smokes.py 存在",
        "scripts/run_p10_dify_safe_package_summary.py 存在",
        "fcf/api/dify_global_regression_api.py 存在",
        "fcf/api/operator_review_response_templates.py 存在",
        "立即停止",
        "不进入下一阶段",
        "不解释为交易信号",
        "不连接真实交易所",
        "不配置 API key",
        "不读取钱包私钥",
        "不尝试真实下单",
        "docs/94_p10_failure_triage_guide.md",
    ]:
        assert item in text


def test_p11_operator_handoff_package_current_package_summary_still_completed():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["package_summary"]["ready_for_p10_d10_bridge_plan"] is True
    assert result["package_summary"]["dify_global_regression_ok"] is True
    assert result["package_summary"]["operator_response_passed"] is True
    assert result["package_summary"]["safe_boundary_ok"] is True


def test_p11_operator_handoff_package_adapter_and_template_still_pass():
    api_response = handle_dify_global_regression_request(
        {
            "request_id": "p11-d2-handoff",
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
    assert api_response["data"]["operator_review_required"] is True
    assert api_response["data"]["ready_for_operator_review"] is True
    assert api_response["data"]["safe_boundary"]["real_execution"] is False
    assert api_response["data"]["safe_boundary"]["bypass_operator_review"] is False
    assert user_response["response_type"] == "global_regression_passed"
    assert user_response["fields"]["real_execution"] is False
    assert user_response["fields"]["bypass_policy_risk_safe_boundary"] is False


def test_p11_operator_handoff_package_mentions_safety_and_next_step():
    text = _text()

    for item in [
        "不接真实交易所 API",
        "不保存真实 API key",
        "不读取钱包私钥",
        "不真实下单",
        "不读取真实账户余额",
        "不读取真实仓位",
        "不声明真实成交",
        "不声明真实资金影响",
        "不配置 CI secret",
        "不做 production deployment",
        "不自动实盘交易",
        "不自动绕过人工复核",
        "不绕过 policy / risk / safe_boundary",
        "不把 paper-only passed 解释成真实交易信号",
        "不把 paper-only passed 解释成真实成交",
        "P11-D3",
        "versioned run commands document",
    ]:
        assert item in text
