from pathlib import Path

from scripts.run_p12_final_delivery_package_summary import run_smoke


DOC = Path("docs/124_archive_d4_final_archive_manifest.md")


def _text():
    return DOC.read_text(encoding="utf-8")


def test_archive_d4_final_archive_manifest_doc_exists():
    text = _text()

    assert DOC.exists()
    assert "Archive-D4" in text
    assert "Final Archive Manifest" in text


def test_archive_d4_final_archive_manifest_mentions_version_and_scope():
    text = _text()

    for item in [
        "final_archive_manifest_version = 0.1.0",
        "archive_mode = immutable_non_production_snapshot",
        "paper_only = true",
        "phase = Final Archive",
        "day = Archive-D4",
        "status = active",
        "final archive manifest",
        "immutable delivery snapshot record",
        "final release note linkage",
        "final operator archive handoff",
        "final non-production delivery preservation",
        "long-term audit readability",
        "paper-only safety preservation",
    ]:
        assert item in text


def test_archive_d4_final_archive_manifest_mentions_archive_source():
    text = _text()

    for item in [
        "source_branch = main",
        "source_remote = origin/main",
        "source_commit = recorded at archive time",
        "source_commit_pushed = true",
        "git_status_clean = true",
        "pytest_result = passed",
        "archive_mode = immutable_non_production_snapshot",
        "production_deployment = false",
        "real_execution = false",
    ]:
        assert item in text


def test_archive_d4_final_archive_manifest_mentions_final_delivery_files():
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
    ]:
        assert item in text


def test_archive_d4_final_archive_manifest_mentions_scripts_package_fixtures_and_tests():
    text = _text()

    for item in [
        "scripts/run_all_smokes.py",
        "scripts/run_p10_dify_safe_package_summary.py",
        "scripts/run_p11_acceptance_smoke.py",
        "scripts/run_p11_release_readiness_package_summary.py",
        "scripts/run_p12_acceptance_smoke.py",
        "scripts/run_p12_final_delivery_package_summary.py",
        "fcf/api/dify_global_regression_api.py",
        "fcf/api/operator_review_response_templates.py",
        "fcf/regression/regression_stability_gate.py",
        "fcf/regression/global_safe_boundary_checker.py",
        "fcf/regression/project_state_consistency_checker.py",
        "fcf/policy/portfolio_risk_guardian.py",
        "fixtures/paper_order_portfolios_multi_asset.json",
        "fixtures/paper_orders_multi_asset_guarded.json",
        "fixtures/multi_asset_market_inputs.json",
        "tests/test_archive_d1_final_archive_plan.py",
        "tests/test_archive_d2_immutable_delivery_snapshot_checklist.py",
        "tests/test_archive_d3_final_release_note.py",
        "tests/test_archive_d4_final_archive_manifest.py",
    ]:
        assert item in text


def test_archive_d4_final_archive_manifest_mentions_final_commands_and_record():
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
        "final_archive_manifest_version",
        "source_branch",
        "source_remote",
        "source_commit",
        "test_count",
        "safe_boundary_ok",
        "operator_review_required",
        "archive_reviewer",
        "archive_timestamp",
        "archive_notes",
    ]:
        assert item in text


def test_archive_d4_final_archive_manifest_mentions_release_note_linkage_and_operator_handoff():
    text = _text()

    for item in [
        "docs/123_archive_d3_final_release_note.md",
        "docs/122_archive_d2_immutable_delivery_snapshot_checklist.md",
        "docs/121_archive_d1_final_archive_plan.md",
        "docs/119_p12_post_closeout_final_delivery_package_summary.md",
        "docs/115_p12_final_safety_boundary_declaration.md",
        "docs/116_p12_final_operator_delivery_note.md",
        "archived package is paper-only",
        "archived package is non-production",
        "archived package requires operator review",
        "archived package cannot place real orders",
        "archived package cannot connect to real exchange",
        "archived package cannot read wallet private key",
        "archived package cannot read real account balance",
        "archived package cannot read real position",
        "archived package cannot bypass policy / risk / safe_boundary",
        "passed results cannot be interpreted as real trade signals",
        "passed results cannot be interpreted as real fills",
    ]:
        assert item in text


def test_archive_d4_final_archive_manifest_mentions_immutable_and_failed_rules():
    text = _text()

    for item in [
        "不回改历史 commit",
        "不 force push 覆盖已归档 commit",
        "不删除测试",
        "不删除安全边界",
        "不删除 failed 停止规则",
        "不删除 operator_review_required",
        "不删除 safe_boundary",
        "不把 archived package 解释成 production deployment",
        "不把 archived package 解释成 live trading package",
        "后续任何修改必须新建 commit",
        "后续任何修改必须重新运行 pytest",
        "后续任何修改必须重新生成 archive manifest",
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


def test_archive_d4_final_archive_manifest_keeps_safety_boundaries():
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


def test_archive_d4_final_archive_manifest_summary_still_ready_and_next_step():
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
    assert "Archive-D5" in text
    assert "final operator archive handoff" in text
