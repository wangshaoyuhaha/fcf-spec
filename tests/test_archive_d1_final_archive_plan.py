from pathlib import Path

from scripts.run_p12_final_delivery_package_summary import run_smoke


DOC = Path("docs/121_archive_d1_final_archive_plan.md")


def _text():
    return DOC.read_text(encoding="utf-8")


def test_archive_d1_final_archive_plan_doc_exists():
    text = _text()

    assert DOC.exists()
    assert "Archive-D1" in text
    assert "Final Archive Plan" in text


def test_archive_d1_final_archive_plan_mentions_version_and_theme():
    text = _text()

    for item in [
        "final_archive_plan_version = 0.1.0",
        "archive_mode = immutable_non_production_snapshot",
        "paper_only = true",
        "phase = Final Archive",
        "day = Archive-D1",
        "status = active",
        "Final archive readiness, immutable delivery snapshot, and operator archive handoff",
        "最终归档准备、不可变交付快照与 operator 归档交接",
    ]:
        assert item in text


def test_archive_d1_final_archive_plan_mentions_current_basis_and_commands():
    text = _text()

    for item in [
        "Phase 9 global paper-only regression suite",
        "Phase 10 Dify-safe paper operations package",
        "Phase 11 release readiness / operator handoff / maintainability package",
        "Phase 12 documentation hardening / archive readiness / final non-production delivery package",
        "P12 final delivery package summary completed",
        "ready_for_p12_d10_archive_bridge_plan true",
        "python main.py",
        "python scripts/run_p12_acceptance_smoke.py",
        "python scripts/run_p12_final_delivery_package_summary.py",
        "python -m pytest -q",
    ]:
        assert item in text


def test_archive_d1_final_archive_plan_mentions_archive_route():
    text = _text()

    for day in [
        "Archive-D1",
        "Archive-D2",
        "Archive-D3",
        "Archive-D4",
        "Archive-D5",
        "Archive-D6",
        "Archive-D7",
    ]:
        assert day in text

    for item in [
        "final archive plan",
        "immutable delivery snapshot checklist",
        "final release note",
        "final archive manifest",
        "final operator archive handoff",
        "final archive acceptance smoke",
        "final archive closeout",
    ]:
        assert item in text


def test_archive_d1_final_archive_plan_mentions_immutable_snapshot_principles():
    text = _text()

    for item in [
        "snapshot 来自 main 分支",
        "snapshot 来自已 push commit",
        "snapshot 对应 pytest 全部 passed",
        "snapshot 对应 git status --short 干净",
        "snapshot 包含 README.md",
        "snapshot 包含 PROJECT_STATE.md",
        "snapshot 包含 docs",
        "snapshot 包含 scripts",
        "snapshot 包含 fcf package",
        "snapshot 包含 fixtures",
        "snapshot 包含 tests",
        "snapshot 包含 final safety boundary declaration",
        "snapshot 包含 final operator delivery note",
        "snapshot 包含 final delivery package summary",
        "不回改历史 commit",
        "不删除测试",
        "不删除安全边界",
        "不删除 failed 停止规则",
        "后续任何修改必须新建 commit",
        "后续任何修改必须重新运行 pytest",
    ]:
        assert item in text


def test_archive_d1_final_archive_plan_mentions_archive_record_fields():
    text = _text()

    for item in [
        "archive_plan_version",
        "archive_mode",
        "paper_only",
        "source_branch",
        "source_commit",
        "source_remote",
        "pytest_result",
        "test_count",
        "command_results",
        "delivery_package_status",
        "ready_for_p12_d10_archive_bridge_plan",
        "safe_boundary_status",
        "operator_review_required",
        "final_archive_reviewer",
        "archive_timestamp",
        "archive_notes",
    ]:
        assert item in text


def test_archive_d1_final_archive_plan_mentions_operator_handoff_and_failed_rules():
    text = _text()

    for item in [
        "paper-only / non-production archived delivery package",
        "不是 production deployment",
        "不是 live trading package",
        "不是 exchange execution package",
        "不是 wallet custody package",
        "不是 real-money trading package",
        "所有 passed 只能说明 paper-only / non-production regression passed",
        "所有结果必须经过人工复核",
        "不能绕过 policy / risk / safe_boundary",
        "立即停止",
        "不进入归档状态",
        "不进入下一阶段",
        "不解释为交易信号",
        "不连接真实交易所",
        "不配置 API key",
        "不读取钱包私钥",
        "不尝试真实下单",
        "docs/94_p10_failure_triage_guide.md",
    ]:
        assert item in text


def test_archive_d1_final_archive_plan_keeps_safety_boundaries():
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


def test_archive_d1_final_archive_plan_summary_still_ready_and_next_step():
    result = run_smoke()
    text = _text()

    assert result["status"] == "completed"
    assert result["package_summary"]["ready_for_p12_d10_archive_bridge_plan"] is True
    assert result["package_summary"]["p12_acceptance_completed"] is True
    assert result["package_summary"]["ready_for_p12_d8_closeout"] is True
    assert result["package_summary"]["p11_release_readiness_summary_completed"] is True
    assert result["package_summary"]["ready_for_p11_d10_bridge_plan"] is True
    assert result["package_summary"]["deliverables_all_present"] is True
    assert result["package_summary"]["safe_boundary_ok"] is True
    assert "Archive-D2" in text
    assert "immutable delivery snapshot checklist" in text
