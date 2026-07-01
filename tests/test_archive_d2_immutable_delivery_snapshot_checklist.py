from pathlib import Path

from scripts.run_p12_final_delivery_package_summary import run_smoke


DOC = Path("docs/122_archive_d2_immutable_delivery_snapshot_checklist.md")


def _text():
    return DOC.read_text(encoding="utf-8")


def test_archive_d2_immutable_snapshot_doc_exists():
    text = _text()

    assert DOC.exists()
    assert "Archive-D2" in text
    assert "Immutable Delivery Snapshot Checklist" in text


def test_archive_d2_immutable_snapshot_mentions_version_and_scope():
    text = _text()

    for item in [
        "immutable_snapshot_checklist_version = 0.1.0",
        "archive_mode = immutable_non_production_snapshot",
        "paper_only = true",
        "phase = Final Archive",
        "day = Archive-D2",
        "status = active",
        "immutable delivery snapshot readiness",
        "final archive readiness",
        "source branch verification",
        "source commit verification",
        "command result verification",
        "safe_boundary preservation",
        "operator archive handoff",
    ]:
        assert item in text


def test_archive_d2_immutable_snapshot_mentions_source_snapshot_checklist():
    text = _text()

    for item in [
        "source_branch = main",
        "source_remote = origin/main",
        "source_commit 已记录",
        "source_commit 已 push",
        "source_commit 可在 GitHub 查看",
        "git status --short 干净",
        "main 与 origin/main 一致",
        "无未提交文件",
        "无未跟踪临时文件",
        "无本地-only 变更",
    ]:
        assert item in text


def test_archive_d2_immutable_snapshot_mentions_command_results():
    text = _text()

    for item in [
        "python main.py",
        "python scripts/run_p12_acceptance_smoke.py",
        "python scripts/run_p12_final_delivery_package_summary.py",
        "python -m pytest -q",
        "events_recorded: 8",
        "status completed",
        "ready_for_p12_d8_closeout true",
        "ready_for_p12_d10_archive_bridge_plan true",
        "pytest 全部 passed",
        "no failed tests",
        "no skipped required checks",
        "no safe_boundary violations",
    ]:
        assert item in text


def test_archive_d2_immutable_snapshot_mentions_deliverables():
    text = _text()

    for item in [
        "README.md",
        "PROJECT_STATE.md",
        "docs/111_p12_final_non_production_delivery_package.md",
        "docs/112_p12_archive_readiness_checklist.md",
        "docs/113_p12_final_command_index.md",
        "docs/114_p12_final_artifact_manifest.md",
        "docs/115_p12_final_safety_boundary_declaration.md",
        "docs/116_p12_final_operator_delivery_note.md",
        "docs/117_p12_acceptance_smoke.md",
        "docs/118_p12_closeout_project_state.md",
        "docs/119_p12_post_closeout_final_delivery_package_summary.md",
        "docs/120_p12_to_final_archive_bridge_plan.md",
        "docs/121_archive_d1_final_archive_plan.md",
        "docs/122_archive_d2_immutable_delivery_snapshot_checklist.md",
        "scripts/run_p12_acceptance_smoke.py",
        "scripts/run_p12_final_delivery_package_summary.py",
        "tests/test_archive_d1_final_archive_plan.py",
        "tests/test_archive_d2_immutable_delivery_snapshot_checklist.py",
    ]:
        assert item in text


def test_archive_d2_immutable_snapshot_mentions_safe_boundary_fields():
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


def test_archive_d2_immutable_snapshot_mentions_operator_review_and_record_fields():
    text = _text()

    for item in [
        "operator_review_required true",
        "ready_for_operator_review true",
        "bypass_operator_review false",
        "bypass_policy_risk_safe_boundary false",
        "operator 只能读取 paper-only / non-production 结果",
        "operator 不能解释为真实交易信号",
        "operator 不能解释为真实成交",
        "operator 不能连接真实交易所",
        "operator 不能配置真实 API key",
        "operator 不能读取钱包私钥",
        "operator 不能真实下单",
        "immutable_snapshot_checklist_version",
        "source_branch",
        "source_remote",
        "source_commit",
        "source_commit_pushed",
        "git_status_clean",
        "pytest_result",
        "test_count",
        "p12_acceptance_status",
        "final_delivery_package_summary_status",
        "archive_snapshot_reviewer",
        "archive_snapshot_timestamp",
        "archive_snapshot_notes",
    ]:
        assert item in text


def test_archive_d2_immutable_snapshot_mentions_immutable_and_failed_rules():
    text = _text()

    for item in [
        "不回改历史 commit",
        "不 force push 覆盖已归档 commit",
        "不删除测试",
        "不删除安全边界",
        "不删除 failed 停止规则",
        "不删除 operator_review_required",
        "不删除 safe_boundary",
        "不把 archived snapshot 解释成 production deployment",
        "不把 archived snapshot 解释成 live trading package",
        "后续任何修改必须新建 commit",
        "后续任何修改必须重新运行 pytest",
        "后续任何修改必须重新生成 archive record",
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


def test_archive_d2_immutable_snapshot_keeps_safety_boundaries():
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


def test_archive_d2_immutable_snapshot_summary_still_ready_and_next_step():
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
    assert "Archive-D3" in text
    assert "final release note" in text
