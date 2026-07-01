from pathlib import Path

from scripts.run_p11_release_readiness_package_summary import run_smoke


DOC = Path("docs/112_p12_archive_readiness_checklist.md")


def _text():
    return DOC.read_text(encoding="utf-8")


def test_p12_archive_readiness_checklist_doc_exists():
    text = _text()

    assert DOC.exists()
    assert "P12-D3" in text
    assert "Archive Readiness Checklist" in text


def test_p12_archive_readiness_checklist_mentions_version_and_scope():
    text = _text()

    for item in [
        "archive_checklist_version = 0.1.0",
        "archive_mode = non_production",
        "paper_only = true",
        "phase = P12",
        "day = P12-D3",
        "status = active",
        "archive readiness review",
        "final non-production delivery review",
        "release readiness review",
        "operator handoff review",
        "regression stability review",
        "documentation hardening review",
    ]:
        assert item in text


def test_p12_archive_readiness_checklist_mentions_repository_readiness():
    text = _text()

    for item in [
        "Repository readiness checklist",
        "当前分支为 main",
        "main 与 origin/main 一致",
        "git status --short 干净",
        "最近一次 commit 已完成",
        "最近一次 push 已完成",
        "无未提交 docs",
        "无未提交 tests",
        "无未提交 scripts",
        "无未提交 fcf package 文件",
        "无临时调试文件",
    ]:
        assert item in text


def test_p12_archive_readiness_checklist_mentions_documentation_readiness():
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
        "docs/112_p12_archive_readiness_checklist.md",
    ]:
        assert item in text


def test_p12_archive_readiness_checklist_mentions_command_readiness():
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


def test_p12_archive_readiness_checklist_mentions_package_readiness():
    text = _text()

    for item in [
        "final non-production delivery package exists",
        "P11 release readiness package summary completed",
        "ready_for_p11_d10_bridge_plan true",
        "P11 acceptance smoke completed",
        "ready_for_p11_d8_closeout true",
        "regression stability gate completed",
        "regression stability gate ok true",
        "operator handoff package exists",
        "versioned run commands document exists",
        "artifact inventory exists",
        "maintenance checklist exists",
        "safe_boundary ok true",
    ]:
        assert item in text


def test_p12_archive_readiness_checklist_mentions_artifact_and_record_readiness():
    text = _text()

    for item in [
        "docs artifact 已记录",
        "scripts artifact 已记录",
        "api artifact 已记录",
        "regression artifact 已记录",
        "policy artifact 已记录",
        "fixtures artifact 已记录",
        "tests artifact 已记录",
        "artifact owner 已记录",
        "artifact status 已记录",
        "deprecated artifact 已说明替代 artifact",
        "docs/103_p11_artifact_inventory.md",
        "docs/111_p12_final_non_production_delivery_package.md",
        "P12-D5 final artifact manifest",
        "archive_checklist_version",
        "archive_mode = non_production",
        "final_delivery_package",
        "command_index",
        "artifact_manifest",
        "safety_boundary_declaration",
        "operator_delivery_note",
        "archive_readiness_status",
    ]:
        assert item in text


def test_p12_archive_readiness_checklist_mentions_failed_rules_and_safety():
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


def test_p12_archive_readiness_checklist_mentions_safe_boundary_fields():
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


def test_p12_archive_readiness_checklist_p11_summary_still_ready_and_next_step():
    result = run_smoke()
    text = _text()

    assert result["status"] == "completed"
    assert result["package_summary"]["ready_for_p11_d10_bridge_plan"] is True
    assert result["package_summary"]["p11_acceptance_completed"] is True
    assert result["package_summary"]["regression_stability_gate_ok"] is True
    assert result["package_summary"]["safe_boundary_ok"] is True
    assert "P12-D4" in text
    assert "final command index" in text
