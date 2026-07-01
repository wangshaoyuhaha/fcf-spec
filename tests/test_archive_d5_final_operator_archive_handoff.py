from pathlib import Path

from scripts.run_p12_final_delivery_package_summary import run_smoke


DOC = Path("docs/125_archive_d5_final_operator_archive_handoff.md")


def _text():
    return DOC.read_text(encoding="utf-8")


def test_archive_d5_final_operator_archive_handoff_doc_exists():
    text = _text()

    assert DOC.exists()
    assert "Archive-D5" in text
    assert "Final Operator Archive Handoff" in text


def test_archive_d5_final_operator_archive_handoff_mentions_version_and_scope():
    text = _text()

    for item in [
        "final_operator_archive_handoff_version = 0.1.0",
        "archive_mode = immutable_non_production_snapshot",
        "paper_only = true",
        "phase = Final Archive",
        "day = Archive-D5",
        "status = active",
        "final operator archive handoff",
        "final archive readiness",
        "immutable delivery snapshot review",
        "archived package reading guide",
        "long-term audit readability",
        "paper-only safety preservation",
    ]:
        assert item in text


def test_archive_d5_final_operator_archive_handoff_mentions_operator_can_do():
    text = _text()

    for item in [
        "operator 可以做",
        "读取 README.md",
        "读取 PROJECT_STATE.md",
        "读取 final release note",
        "读取 final archive manifest",
        "读取 immutable delivery snapshot checklist",
        "运行 python main.py",
        "运行 python scripts/run_p12_acceptance_smoke.py",
        "运行 python scripts/run_p12_final_delivery_package_summary.py",
        "运行 python -m pytest -q",
        "读取 status completed",
        "读取 ready_for_p12_d8_closeout true",
        "读取 ready_for_p12_d10_archive_bridge_plan true",
        "读取 safe_boundary ok true",
        "进入人工复核",
        "做 archive readiness review",
    ]:
        assert item in text


def test_archive_d5_final_operator_archive_handoff_mentions_operator_cannot_do():
    text = _text()

    for item in [
        "operator 不可以做",
        "真实交易",
        "实盘下单",
        "真实账户读取",
        "真实仓位读取",
        "钱包私钥读取",
        "配置真实 API key",
        "连接真实交易所",
        "声明真实成交",
        "声明真实资金影响",
        "production deployment",
        "自动实盘交易",
        "自动绕过人工复核",
        "绕过 policy / risk / safe_boundary",
        "把 paper-only passed 解释成真实交易信号",
        "把 paper-only passed 解释成真实成交",
    ]:
        assert item in text


def test_archive_d5_final_operator_archive_handoff_mentions_handoff_files():
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
        "docs/123_archive_d3_final_release_note.md",
        "docs/124_archive_d4_final_archive_manifest.md",
        "docs/125_archive_d5_final_operator_archive_handoff.md",
    ]:
        assert item in text


def test_archive_d5_final_operator_archive_handoff_mentions_commands_and_archive_record():
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
        "git status --short 干净",
        "commit 已完成",
        "push 已完成",
        "source_branch = main",
        "source_remote = origin/main",
        "source_commit 已记录",
        "source_commit 已 push",
        "source_commit 可在 GitHub 查看",
        "git_status_clean true",
        "pytest_result passed",
        "test_count 已记录",
        "production_deployment false",
        "real_execution false",
    ]:
        assert item in text


def test_archive_d5_final_operator_archive_handoff_mentions_allowed_and_forbidden_interpretation():
    text = _text()

    for item in [
        "paper-only local regression passed",
        "non-production validation passed",
        "Dify-safe operator review package ready",
        "release readiness review ready",
        "archive readiness review ready",
        "final non-production delivery package ready",
        "immutable delivery snapshot can be reviewed",
        "operator review required",
        "manual review required",
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


def test_archive_d5_final_operator_archive_handoff_mentions_review_and_safe_boundary():
    text = _text()

    for item in [
        "operator_review_required = true",
        "ready_for_operator_review = true",
        "bypass_operator_review = false",
        "bypass_policy_risk_safe_boundary = false",
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
        "auto_live_trading = false",
    ]:
        assert item in text


def test_archive_d5_final_operator_archive_handoff_mentions_failed_and_post_archive_rules():
    text = _text()

    for item in [
        "立即停止",
        "不进入归档状态",
        "不进入下一阶段",
        "不解释为交易信号",
        "不连接真实交易所",
        "不配置 API key",
        "不读取钱包私钥",
        "不尝试真实下单",
        "不删除测试绕过失败",
        "不修改 safe_boundary 绕过失败",
        "不绕过人工复核",
        "不绕过 policy / risk / safe_boundary",
        "docs/94_p10_failure_triage_guide.md",
        "新建 commit",
        "重新运行 python main.py",
        "重新运行 python scripts/run_p12_acceptance_smoke.py",
        "重新运行 python scripts/run_p12_final_delivery_package_summary.py",
        "重新运行 python -m pytest -q",
        "重新更新 PROJECT_STATE.md",
        "重新更新 archive record",
        "重新 push",
        "回改历史 commit",
        "force push 覆盖已归档 commit",
    ]:
        assert item in text


def test_archive_d5_final_operator_archive_handoff_keeps_safety_boundaries():
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


def test_archive_d5_final_operator_archive_handoff_summary_still_ready_and_next_step():
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
    assert "Archive-D6" in text
    assert "final archive acceptance smoke" in text
