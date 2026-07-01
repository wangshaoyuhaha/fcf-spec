from pathlib import Path

from scripts.run_p10_dify_safe_package_summary import run_smoke


DOC = Path("docs/103_p11_artifact_inventory.md")


def _text():
    return DOC.read_text(encoding="utf-8")


def test_p11_artifact_inventory_doc_exists():
    text = _text()

    assert DOC.exists()
    assert "P11-D4" in text
    assert "Artifact Inventory and Ownership Map" in text


def test_p11_artifact_inventory_mentions_version_and_purpose():
    text = _text()

    for item in [
        "inventory_version = 0.1.0",
        "phase = P11",
        "day = P11-D4",
        "status = active",
        "release readiness",
        "operator handoff",
        "long-term maintainability",
        "regression stability review",
        "paper-only safety review",
    ]:
        assert item in text


def test_p11_artifact_inventory_mentions_owner_roles():
    text = _text()

    for item in [
        "owner = operator",
        "owner = maintainer",
        "owner = reviewer",
        "owner = safety_guardian",
        "运行命令",
        "修改代码",
        "检查 operator handoff package",
        "检查 safe_boundary",
    ]:
        assert item in text


def test_p11_artifact_inventory_mentions_core_docs():
    text = _text()

    for item in [
        "README.md | owner = maintainer | status = active",
        "PROJECT_STATE.md | owner = maintainer | status = active",
        "docs/100_p11_release_readiness_plan.md | owner = reviewer | status = active",
        "docs/101_p11_operator_handoff_package.md | owner = operator | status = active",
        "docs/102_p11_versioned_run_commands.md | owner = operator | status = active",
        "docs/103_p11_artifact_inventory.md | owner = maintainer | status = active",
    ]:
        assert item in text


def test_p11_artifact_inventory_mentions_p10_dify_package_docs():
    text = _text()

    for item in [
        "docs/90_p10_dify_safe_paper_operations_plan.md",
        "docs/91_p10_global_regression_dify_adapter_contract.md",
        "docs/92_p10_operator_review_response_templates.md",
        "docs/93_p10_paper_only_operator_runbook.md",
        "docs/94_p10_failure_triage_guide.md",
        "docs/95_p10_dify_workflow_node_contract.md",
        "docs/96_p10_acceptance_smoke.md",
        "docs/97_p10_closeout_project_state.md",
        "docs/98_p10_post_closeout_dify_safe_package_summary.md",
        "docs/99_p10_to_p11_bridge_plan.md",
    ]:
        assert item in text


def test_p11_artifact_inventory_mentions_scripts_api_regression_and_fixtures():
    text = _text()

    for item in [
        "scripts/run_all_smokes.py",
        "scripts/run_p9_global_regression_summary.py",
        "scripts/run_p10_acceptance_smoke.py",
        "scripts/run_p10_dify_safe_package_summary.py",
        "fcf/api/dify_global_regression_api.py",
        "fcf/api/operator_review_response_templates.py",
        "fcf/api/portfolio_paper_execution_api.py",
        "fcf/regression/global_regression_report_schema.py",
        "fcf/regression/global_safe_boundary_checker.py",
        "fcf/regression/project_state_consistency_checker.py",
        "fcf/policy/portfolio_risk_guardian.py",
        "fixtures/paper_order_portfolios_multi_asset.json",
        "fixtures/paper_orders_multi_asset_guarded.json",
    ]:
        assert item in text


def test_p11_artifact_inventory_mentions_tests():
    text = _text()

    for item in [
        "tests/test_p11_release_readiness_plan.py",
        "tests/test_p11_operator_handoff_package.py",
        "tests/test_p11_versioned_run_commands.py",
        "tests/test_p11_artifact_inventory.py",
        "tests/test_p10_dify_safe_package_summary.py",
        "tests/test_p10_acceptance_smoke.py",
    ]:
        assert item in text


def test_p11_artifact_inventory_mentions_maintenance_rules():
    text = _text()

    for item in [
        "新增 artifact 必须写入 inventory",
        "修改 artifact 必须更新对应测试",
        "删除 artifact 必须标记 deprecated",
        "deprecated artifact 必须说明替代 artifact",
        "README.md 和 PROJECT_STATE.md 必须同步更新",
        "每次变更必须运行 python -m pytest -q",
        "每次阶段完成必须 commit",
        "每次阶段完成必须 push",
        "不允许删除安全边界",
        "不允许删除 failed 停止规则",
        "不允许绕过测试",
    ]:
        assert item in text


def test_p11_artifact_inventory_current_package_summary_still_completed():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["package_summary"]["ready_for_p10_d10_bridge_plan"] is True
    assert result["package_summary"]["deliverables_all_present"] is True
    assert result["package_summary"]["safe_boundary_ok"] is True


def test_p11_artifact_inventory_mentions_safety_and_next_step():
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
        "P11-D5",
        "maintenance checklist",
    ]:
        assert item in text
