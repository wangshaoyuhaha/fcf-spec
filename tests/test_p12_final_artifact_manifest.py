from pathlib import Path

from scripts.run_p11_release_readiness_package_summary import run_smoke


DOC = Path("docs/114_p12_final_artifact_manifest.md")


def _text():
    return DOC.read_text(encoding="utf-8")


def test_p12_final_artifact_manifest_doc_exists():
    text = _text()

    assert DOC.exists()
    assert "P12-D5" in text
    assert "Final Artifact Manifest" in text


def test_p12_final_artifact_manifest_mentions_version_and_scope():
    text = _text()

    for item in [
        "final_artifact_manifest_version = 0.1.0",
        "manifest_mode = non_production",
        "paper_only = true",
        "phase = P12",
        "day = P12-D5",
        "status = active",
        "final non-production delivery",
        "archive readiness review",
        "documentation hardening review",
        "operator handoff review",
        "release readiness review",
        "regression stability review",
    ]:
        assert item in text


def test_p12_final_artifact_manifest_mentions_owner_and_status_rules():
    text = _text()

    for item in [
        "owner = operator",
        "owner = maintainer",
        "owner = reviewer",
        "owner = safety_guardian",
        "status = active",
        "status = deprecated",
        "status = planned",
        "每个 final artifact 必须有 path",
        "每个 final artifact 必须有 owner",
        "每个 final artifact 必须有 status",
        "deprecated artifact 必须说明 replacement artifact",
        "planned artifact 必须说明 planned phase",
        "新增 artifact 必须同步 README.md",
        "新增 artifact 必须同步 PROJECT_STATE.md",
        "新增 artifact 必须增加测试",
    ]:
        assert item in text


def test_p12_final_artifact_manifest_mentions_docs_manifest():
    text = _text()

    for item in [
        "README.md | owner = maintainer | status = active",
        "PROJECT_STATE.md | owner = maintainer | status = active",
        "docs/93_p10_paper_only_operator_runbook.md | owner = operator | status = active",
        "docs/94_p10_failure_triage_guide.md | owner = operator | status = active",
        "docs/100_p11_release_readiness_plan.md | owner = reviewer | status = active",
        "docs/101_p11_operator_handoff_package.md | owner = operator | status = active",
        "docs/102_p11_versioned_run_commands.md | owner = operator | status = active",
        "docs/103_p11_artifact_inventory.md | owner = maintainer | status = active",
        "docs/111_p12_final_non_production_delivery_package.md | owner = reviewer | status = active",
        "docs/112_p12_archive_readiness_checklist.md | owner = reviewer | status = active",
        "docs/113_p12_final_command_index.md | owner = operator | status = active",
        "docs/114_p12_final_artifact_manifest.md | owner = maintainer | status = active",
    ]:
        assert item in text


def test_p12_final_artifact_manifest_mentions_scripts_api_regression_policy_and_fixtures():
    text = _text()

    for item in [
        "scripts/run_all_smokes.py | owner = maintainer | status = active",
        "scripts/run_p10_dify_safe_package_summary.py | owner = maintainer | status = active",
        "scripts/run_p11_acceptance_smoke.py | owner = maintainer | status = active",
        "scripts/run_p11_release_readiness_package_summary.py | owner = maintainer | status = active",
        "fcf/api/dify_global_regression_api.py | owner = maintainer | status = active",
        "fcf/api/operator_review_response_templates.py | owner = maintainer | status = active",
        "fcf/regression/global_safe_boundary_checker.py | owner = safety_guardian | status = active",
        "fcf/regression/project_state_consistency_checker.py | owner = safety_guardian | status = active",
        "fcf/regression/regression_stability_gate.py | owner = safety_guardian | status = active",
        "fcf/policy/portfolio_risk_guardian.py | owner = safety_guardian | status = active",
        "fixtures/paper_order_portfolios_multi_asset.json | owner = maintainer | status = active",
        "fixtures/paper_orders_multi_asset_guarded.json | owner = maintainer | status = active",
    ]:
        assert item in text


def test_p12_final_artifact_manifest_mentions_tests_manifest():
    text = _text()

    for item in [
        "tests/test_p11_release_readiness_plan.py | owner = maintainer | status = active",
        "tests/test_p11_acceptance_smoke.py | owner = maintainer | status = active",
        "tests/test_p11_release_readiness_package_summary.py | owner = maintainer | status = active",
        "tests/test_p11_to_p12_bridge_plan.py | owner = maintainer | status = active",
        "tests/test_p12_documentation_hardening_plan.py | owner = maintainer | status = active",
        "tests/test_p12_final_non_production_delivery_package.py | owner = maintainer | status = active",
        "tests/test_p12_archive_readiness_checklist.py | owner = maintainer | status = active",
        "tests/test_p12_final_command_index.py | owner = maintainer | status = active",
        "tests/test_p12_final_artifact_manifest.py | owner = maintainer | status = active",
    ]:
        assert item in text


def test_p12_final_artifact_manifest_mentions_planned_and_deprecated_rules():
    text = _text()

    for item in [
        "docs/115_p12_final_safety_boundary_declaration.md | owner = safety_guardian | status = planned | planned phase = P12-D6",
        "docs/116_p12_final_operator_delivery_note.md | owner = operator | status = planned | planned phase = P12-D7",
        "docs/117_p12_acceptance_smoke.md | owner = reviewer | status = planned | planned phase = P12-D7",
        "scripts/run_p12_acceptance_smoke.py | owner = maintainer | status = planned | planned phase = P12-D7",
        "docs/118_p12_closeout_project_state.md | owner = reviewer | status = planned | planned phase = P12-D8",
        "当前无 deprecated artifact",
        "deprecated artifact path",
        "replacement artifact path",
        "deprecated reason",
        "deprecated phase",
        "safe removal status",
        "deprecated 不允许用于绕过测试",
        "deprecated 不允许用于删除安全边界",
        "deprecated 不允许用于删除 failed 停止规则",
    ]:
        assert item in text


def test_p12_final_artifact_manifest_mentions_archive_readiness_linkage():
    text = _text()

    for item in [
        "docs/111_p12_final_non_production_delivery_package.md",
        "docs/112_p12_archive_readiness_checklist.md",
        "docs/113_p12_final_command_index.md",
        "docs/114_p12_final_artifact_manifest.md",
        "final non-production delivery package exists",
        "archive readiness checklist exists",
        "final command index exists",
        "final artifact manifest exists",
        "P11 release readiness package summary completed",
        "ready_for_p11_d10_bridge_plan true",
        "pytest 全部 passed",
        "git status --short 干净",
        "commit 已完成",
        "push 已完成",
    ]:
        assert item in text


def test_p12_final_artifact_manifest_mentions_safety_boundaries():
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


def test_p12_final_artifact_manifest_p11_summary_still_ready_and_next_step():
    result = run_smoke()
    text = _text()

    assert result["status"] == "completed"
    assert result["package_summary"]["ready_for_p11_d10_bridge_plan"] is True
    assert result["package_summary"]["p11_acceptance_completed"] is True
    assert result["package_summary"]["regression_stability_gate_ok"] is True
    assert result["package_summary"]["deliverables_all_present"] is True
    assert result["package_summary"]["safe_boundary_ok"] is True
    assert "P12-D6" in text
    assert "final safety boundary declaration" in text
