from pathlib import Path

from scripts.run_p10_dify_safe_package_summary import run_smoke


DOC = Path("docs/104_p11_maintenance_checklist.md")


def _text():
    return DOC.read_text(encoding="utf-8")


def test_p11_maintenance_checklist_doc_exists():
    text = _text()

    assert DOC.exists()
    assert "P11-D5" in text
    assert "Maintenance Checklist" in text


def test_p11_maintenance_checklist_mentions_version_and_purpose():
    text = _text()

    for item in [
        "checklist_version = 0.1.0",
        "phase = P11",
        "day = P11-D5",
        "status = active",
        "daily maintenance",
        "pre-change review",
        "post-change review",
        "pre-release review",
        "safety boundary review",
        "failed triage",
        "long-term maintainability",
    ]:
        assert item in text


def test_p11_maintenance_checklist_mentions_daily_checks():
    text = _text()

    for item in [
        "Daily maintenance checklist",
        "README.md 存在",
        "PROJECT_STATE.md 存在",
        "docs/101_p11_operator_handoff_package.md 存在",
        "docs/102_p11_versioned_run_commands.md 存在",
        "docs/103_p11_artifact_inventory.md 存在",
        "docs/104_p11_maintenance_checklist.md 存在",
        "python main.py 可运行",
        "python scripts/run_all_smokes.py 可运行",
        "python scripts/run_p10_dify_safe_package_summary.py 可运行",
        "python -m pytest -q 可运行",
        "events_recorded: 8",
        "status completed",
        "pytest 全部 passed",
        "git status 干净",
    ]:
        assert item in text


def test_p11_maintenance_checklist_mentions_pre_change_checks():
    text = _text()

    for item in [
        "Pre-change checklist",
        "当前 main 与 origin/main 一致",
        "git status --short 干净",
        "最近一次 pytest 已通过",
        "当前任务属于 paper-only / non-production",
        "当前任务不需要真实交易所 API",
        "当前任务不需要真实 API key",
        "当前任务不需要钱包私钥",
        "当前任务不需要真实账户余额",
        "当前任务不需要真实仓位",
        "当前任务不需要真实下单",
    ]:
        assert item in text


def test_p11_maintenance_checklist_mentions_post_change_checks():
    text = _text()

    for item in [
        "Post-change checklist",
        "新增或修改 docs",
        "新增或修改 tests",
        "README.md 已更新",
        "PROJECT_STATE.md 已更新",
        "artifact inventory 已更新或确认无需更新",
        "versioned run commands 已更新或确认无需更新",
        "python main.py 通过",
        "python scripts/run_p10_dify_safe_package_summary.py 通过",
        "python -m pytest -q 通过",
        "commit 已完成",
        "push 已完成",
    ]:
        assert item in text


def test_p11_maintenance_checklist_mentions_pre_release_checks():
    text = _text()

    for item in [
        "Pre-release checklist",
        "operator handoff package 已存在",
        "versioned run commands document 已存在",
        "artifact inventory 已存在",
        "maintenance checklist 已存在",
        "failure triage guide 已存在",
        "Dify workflow node contract 已存在",
        "run_p10_dify_safe_package_summary 输出 status completed",
        "Dify-safe adapter 输出 ok true",
        "operator review response 输出 global_regression_passed",
        "operator_review_required true",
        "ready_for_operator_review true",
        "safe_boundary ok true",
    ]:
        assert item in text


def test_p11_maintenance_checklist_mentions_safety_boundary_checks():
    text = _text()

    for item in [
        "Safety boundary checklist",
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
        "paper_only = true",
        "execution_mode = paper",
        "real_execution = false",
        "real_exchange_api = false",
        "bypass_operator_review = false",
        "bypass_policy_risk_safe_boundary = false",
    ]:
        assert item in text


def test_p11_maintenance_checklist_mentions_failed_and_long_term_rules():
    text = _text()

    for item in [
        "Failed triage checklist",
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
        "Long-term maintainability checklist",
        "每个阶段有文档",
        "每个阶段有测试",
        "每个阶段有 README.md 更新",
        "每个阶段有 PROJECT_STATE.md 更新",
        "每个阶段有 commit",
        "每个阶段有 push",
        "新 artifact 写入 docs/103_p11_artifact_inventory.md",
        "新命令写入 docs/102_p11_versioned_run_commands.md",
        "安全边界不被删除",
        "paper-only / non-production 声明不被删除",
    ]:
        assert item in text


def test_p11_maintenance_checklist_current_package_summary_still_completed():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["package_summary"]["ready_for_p10_d10_bridge_plan"] is True
    assert result["package_summary"]["deliverables_all_present"] is True
    assert result["package_summary"]["safe_boundary_ok"] is True


def test_p11_maintenance_checklist_mentions_next_step():
    text = _text()

    assert "P11-D6" in text
    assert "regression stability gate" in text
