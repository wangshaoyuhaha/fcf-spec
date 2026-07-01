from pathlib import Path

from fcf.api.dify_global_regression_api import handle_dify_global_regression_request
from fcf.api.operator_review_response_templates import render_operator_review_response
from scripts.run_p10_dify_safe_package_summary import run_smoke


DOC = Path("docs/102_p11_versioned_run_commands.md")


def _text():
    return DOC.read_text(encoding="utf-8")


def test_p11_versioned_run_commands_doc_exists():
    text = _text()

    assert DOC.exists()
    assert "P11-D3" in text
    assert "Versioned Run Commands Document" in text


def test_p11_versioned_run_commands_mentions_profile_version():
    text = _text()

    for item in [
        "command_profile_version = 0.1.0",
        "phase = P11",
        "day = P11-D3",
        "status = active",
        "operator handoff",
        "release readiness",
        "regression stability review",
        "long-term maintenance",
    ]:
        assert item in text


def test_p11_versioned_run_commands_mentions_local_full_regression_profile():
    text = _text()

    for item in [
        "local_full_regression",
        "python main.py",
        "python scripts/run_all_smokes.py",
        "python scripts/run_p9_global_regression_summary.py",
        "python scripts/run_p10_acceptance_smoke.py",
        "python scripts/run_p10_dify_safe_package_summary.py",
        "python -m pytest -q",
        "events_recorded: 8",
        "status completed",
        "全部 passed",
    ]:
        assert item in text


def test_p11_versioned_run_commands_mentions_ci_safe_profile():
    text = _text()

    for item in [
        "ci_safe_regression",
        "不需要 exchange API key",
        "不需要 wallet private key",
        "不需要 real account credentials",
        "不需要 real broker credentials",
        "不需要 CI secret",
        "不需要 production deployment permission",
        "不连接真实交易所",
        "不真实下单",
    ]:
        assert item in text


def test_p11_versioned_run_commands_mentions_dify_safe_paper_review_profile():
    text = _text()

    for item in [
        "dify_safe_paper_review",
        "handle_dify_global_regression_request",
        "render_operator_review_response",
        "review_mode = paper_only",
        "review_mode = operator_review",
        "review_mode = non_production_review",
        "requested_checks = all_smokes",
        "requested_checks = global_report",
        "requested_checks = safe_boundary",
        "requested_checks = project_state_consistency",
        "output_format = json",
        "ready_for_operator_review true",
        "operator_review_required true",
        "response_type = global_regression_passed",
        "safe_boundary.real_execution = false",
        "safe_boundary.real_exchange_api = false",
        "safe_boundary.bypass_operator_review = false",
        "safe_boundary.bypass_policy_risk_safe_boundary = false",
    ]:
        assert item in text


def test_p11_versioned_run_commands_mentions_failure_triage_profile():
    text = _text()

    for item in [
        "failure_triage",
        "docs/94_p10_failure_triage_guide.md",
        "停止继续操作",
        "不进入下一阶段",
        "不解释为交易信号",
        "不连接真实交易所",
        "不配置 API key",
        "不读取钱包私钥",
        "不尝试真实下单",
        "不删除测试绕过失败",
        "不修改 safe_boundary 绕过失败",
    ]:
        assert item in text


def test_p11_versioned_run_commands_mentions_maintenance_rules():
    text = _text()

    for item in [
        "写入 README.md",
        "写入 PROJECT_STATE.md",
        "写入对应 docs 文件",
        "增加测试",
        "运行 python -m pytest -q",
        "commit",
        "push",
        "deprecated",
        "替代命令",
        "不删除安全边界",
        "不删除 failed 停止规则",
    ]:
        assert item in text


def test_p11_versioned_run_commands_current_package_summary_still_completed():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["package_summary"]["ready_for_p10_d10_bridge_plan"] is True
    assert result["package_summary"]["dify_global_regression_ok"] is True
    assert result["package_summary"]["operator_response_passed"] is True
    assert result["package_summary"]["safe_boundary_ok"] is True


def test_p11_versioned_run_commands_dify_entrypoints_still_pass():
    api_response = handle_dify_global_regression_request(
        {
            "request_id": "p11-d3-versioned-commands",
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
    assert api_response["data"]["operator_review_required"] is True
    assert api_response["data"]["safe_boundary"]["real_execution"] is False
    assert api_response["data"]["safe_boundary"]["bypass_operator_review"] is False
    assert user_response["response_type"] == "global_regression_passed"
    assert user_response["fields"]["real_execution"] is False
    assert user_response["fields"]["bypass_policy_risk_safe_boundary"] is False


def test_p11_versioned_run_commands_mentions_safety_and_next_step():
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
        "P11-D4",
        "artifact inventory and ownership map",
    ]:
        assert item in text
