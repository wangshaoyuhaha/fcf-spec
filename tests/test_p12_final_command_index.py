from pathlib import Path

from scripts.run_p11_release_readiness_package_summary import run_smoke


DOC = Path("docs/113_p12_final_command_index.md")


def _text():
    return DOC.read_text(encoding="utf-8")


def test_p12_final_command_index_doc_exists():
    text = _text()

    assert DOC.exists()
    assert "P12-D4" in text
    assert "Final Command Index" in text


def test_p12_final_command_index_mentions_version_and_scope():
    text = _text()

    for item in [
        "final_command_index_version = 0.1.0",
        "command_index_mode = non_production",
        "paper_only = true",
        "phase = P12",
        "day = P12-D4",
        "status = active",
        "local_full_regression",
        "ci_safe_regression",
        "dify_safe_paper_review",
        "release_readiness_review",
        "archive_readiness_review",
        "failure_triage",
    ]:
        assert item in text


def test_p12_final_command_index_mentions_local_full_regression():
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
        "ready_for_p11_d10_bridge_plan true",
        "pytest 全部 passed",
    ]:
        assert item in text


def test_p12_final_command_index_mentions_ci_safe_regression():
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


def test_p12_final_command_index_mentions_dify_safe_paper_review():
    text = _text()

    for item in [
        "dify_safe_paper_review",
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
        "json",
        "response_type = global_regression_passed",
        "real_execution = false",
        "bypass_operator_review = false",
        "bypass_policy_risk_safe_boundary = false",
    ]:
        assert item in text


def test_p12_final_command_index_mentions_release_and_archive_review():
    text = _text()

    for item in [
        "release_readiness_review",
        "P10 package summary status completed",
        "P11 acceptance smoke status completed",
        "P11 release readiness package summary status completed",
        "ready_for_p11_d8_closeout true",
        "ready_for_p11_d10_bridge_plan true",
        "archive_readiness_review",
        "docs/112_p12_archive_readiness_checklist.md",
        "docs/111_p12_final_non_production_delivery_package.md",
        "docs/103_p11_artifact_inventory.md",
        "archive_checklist_version = 0.1.0",
        "archive_mode = non_production",
        "git status --short 干净",
        "commit 已完成",
        "push 已完成",
    ]:
        assert item in text


def test_p12_final_command_index_mentions_failure_triage():
    text = _text()

    for item in [
        "failure_triage",
        "docs/94_p10_failure_triage_guide.md",
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
        "保留完整错误输出",
    ]:
        assert item in text


def test_p12_final_command_index_mentions_command_maintenance_rules():
    text = _text()

    for item in [
        "新增命令必须写入 docs/113_p12_final_command_index.md",
        "新增命令必须写入 README.md",
        "新增命令必须写入 PROJECT_STATE.md",
        "新增命令必须增加测试",
        "修改命令必须同步修改对应文档",
        "删除命令必须标记 deprecated",
        "deprecated 命令必须说明替代命令",
        "每次修改必须运行 python -m pytest -q",
        "每次阶段完成必须 commit",
        "每次阶段完成必须 push",
        "不允许删除安全边界",
        "不允许删除 failed 停止规则",
        "不允许绕过测试",
    ]:
        assert item in text


def test_p12_final_command_index_mentions_safety_boundaries():
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
    ]:
        assert item in text


def test_p12_final_command_index_p11_summary_still_ready_and_next_step():
    result = run_smoke()
    text = _text()

    assert result["status"] == "completed"
    assert result["package_summary"]["ready_for_p11_d10_bridge_plan"] is True
    assert result["package_summary"]["p11_acceptance_completed"] is True
    assert result["package_summary"]["regression_stability_gate_ok"] is True
    assert result["package_summary"]["deliverables_all_present"] is True
    assert result["package_summary"]["safe_boundary_ok"] is True
    assert "P12-D5" in text
    assert "final artifact manifest" in text
