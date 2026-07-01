from pathlib import Path

from scripts.run_p11_release_readiness_package_summary import run_smoke


PLAN_DOC = Path("docs/110_p12_documentation_hardening_plan.md")


def test_p12_documentation_hardening_plan_doc_exists():
    assert PLAN_DOC.exists()


def test_p12_documentation_hardening_plan_mentions_phase12_theme():
    text = PLAN_DOC.read_text(encoding="utf-8")

    assert "P12-D1" in text
    assert "Phase 12" in text
    assert "Documentation hardening, archive readiness, and final non-production delivery package" in text
    assert "文档硬化、归档准备与最终 non-production 交付包" in text


def test_p12_documentation_hardening_plan_mentions_core_targets():
    text = PLAN_DOC.read_text(encoding="utf-8")

    for item in [
        "documentation hardening plan",
        "final non-production delivery package document",
        "archive readiness checklist",
        "final command index",
        "final artifact manifest",
        "final safety boundary declaration",
        "final operator delivery note",
        "Phase 12 acceptance smoke",
    ]:
        assert item in text


def test_p12_documentation_hardening_plan_mentions_planned_docs():
    text = PLAN_DOC.read_text(encoding="utf-8")

    for item in [
        "docs/111_p12_final_non_production_delivery_package.md",
        "docs/112_p12_archive_readiness_checklist.md",
        "docs/113_p12_final_command_index.md",
        "docs/114_p12_final_artifact_manifest.md",
        "docs/115_p12_final_safety_boundary_declaration.md",
        "docs/116_p12_final_operator_delivery_note.md",
    ]:
        assert item in text


def test_p12_documentation_hardening_plan_mentions_phase12_route():
    text = PLAN_DOC.read_text(encoding="utf-8")

    for day in ["P12-D1", "P12-D2", "P12-D3", "P12-D4", "P12-D5", "P12-D6", "P12-D7", "P12-D8"]:
        assert day in text


def test_p12_documentation_hardening_plan_mentions_final_command_profiles():
    text = PLAN_DOC.read_text(encoding="utf-8")

    for item in [
        "local_full_regression",
        "ci_safe_regression",
        "dify_safe_paper_review",
        "release_readiness_review",
        "archive_readiness_review",
        "failure_triage",
    ]:
        assert item in text


def test_p12_documentation_hardening_plan_mentions_safety_boundaries():
    text = PLAN_DOC.read_text(encoding="utf-8")

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


def test_p12_documentation_hardening_plan_p11_summary_still_ready():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["package_summary"]["ready_for_p11_d10_bridge_plan"] is True
    assert result["package_summary"]["p11_acceptance_completed"] is True
    assert result["package_summary"]["regression_stability_gate_ok"] is True
    assert result["package_summary"]["deliverables_all_present"] is True
    assert result["package_summary"]["safe_boundary_ok"] is True
