from pathlib import Path

from scripts.run_p11_release_readiness_package_summary import run_smoke as run_p11_summary
from scripts.run_p12_acceptance_smoke import run_smoke as run_p12_acceptance


DOC = Path("docs/118_p12_closeout_project_state.md")


def _text():
    return DOC.read_text(encoding="utf-8")


def test_p12_closeout_doc_exists():
    text = _text()

    assert DOC.exists()
    assert "P12-D8" in text
    assert "Phase 12 Closeout" in text


def test_p12_closeout_mentions_phase12_theme_and_days():
    text = _text()

    assert "Documentation hardening, archive readiness, and final non-production delivery package" in text
    assert "文档硬化、归档准备与最终 non-production 交付包" in text

    for day in ["P12-D1", "P12-D2", "P12-D3", "P12-D4", "P12-D5", "P12-D6", "P12-D7", "P12-D8"]:
        assert day in text


def test_p12_closeout_mentions_final_delivery_files():
    text = _text()

    for item in [
        "docs/110_p12_documentation_hardening_plan.md",
        "docs/111_p12_final_non_production_delivery_package.md",
        "docs/112_p12_archive_readiness_checklist.md",
        "docs/113_p12_final_command_index.md",
        "docs/114_p12_final_artifact_manifest.md",
        "docs/115_p12_final_safety_boundary_declaration.md",
        "docs/116_p12_final_operator_delivery_note.md",
        "docs/117_p12_acceptance_smoke.md",
        "docs/118_p12_closeout_project_state.md",
        "scripts/run_p12_acceptance_smoke.py",
    ]:
        assert item in text


def test_p12_closeout_mentions_completed_capabilities():
    text = _text()

    for item in [
        "documentation hardening",
        "final non-production delivery package",
        "archive readiness checklist",
        "final command index",
        "final artifact manifest",
        "final safety boundary declaration",
        "final operator delivery note",
        "Phase 12 acceptance smoke",
        "ready_for_p12_d8_closeout=true",
    ]:
        assert item in text


def test_p12_closeout_mentions_final_commands():
    text = _text()

    for item in [
        "python main.py",
        "python scripts/run_all_smokes.py",
        "python scripts/run_p9_global_regression_summary.py",
        "python scripts/run_p10_dify_safe_package_summary.py",
        "python scripts/run_p11_acceptance_smoke.py",
        "python scripts/run_p11_release_readiness_package_summary.py",
        "python scripts/run_p12_acceptance_smoke.py",
        "python -m pytest -q",
    ]:
        assert item in text


def test_p12_closeout_p12_acceptance_still_completed():
    result = run_p12_acceptance()
    summary = result["acceptance_summary"]

    assert result["status"] == "completed"
    assert summary["phase"] == "P12"
    assert summary["ready_for_p11_d10_bridge_plan"] is True
    assert summary["p12_docs_all_present"] is True
    assert summary["safe_boundary_ok"] is True
    assert summary["ready_for_p12_d8_closeout"] is True


def test_p12_closeout_p11_summary_still_completed():
    result = run_p11_summary()

    assert result["status"] == "completed"
    assert result["package_summary"]["ready_for_p11_d10_bridge_plan"] is True
    assert result["package_summary"]["p11_acceptance_completed"] is True
    assert result["package_summary"]["regression_stability_gate_ok"] is True
    assert result["package_summary"]["safe_boundary_ok"] is True


def test_p12_closeout_keeps_safety_boundaries_and_next_steps():
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
        "P12-D9",
        "post-closeout final delivery package summary",
        "P12-D10",
        "Phase 12 to final archive bridge plan",
    ]:
        assert item in text
