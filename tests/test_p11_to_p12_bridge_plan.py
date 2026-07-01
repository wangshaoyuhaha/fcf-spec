from pathlib import Path

from scripts.run_p11_release_readiness_package_summary import run_smoke


BRIDGE_DOC = Path("docs/109_p11_to_p12_bridge_plan.md")


def test_p11_to_p12_bridge_doc_exists():
    assert BRIDGE_DOC.exists()


def test_p11_to_p12_bridge_doc_mentions_p11_days():
    text = BRIDGE_DOC.read_text(encoding="utf-8")

    for day in [
        "P11-D1",
        "P11-D2",
        "P11-D3",
        "P11-D4",
        "P11-D5",
        "P11-D6",
        "P11-D7",
        "P11-D8",
        "P11-D9",
        "P11-D10",
    ]:
        assert day in text


def test_p11_to_p12_bridge_doc_mentions_phase12_theme_and_route():
    text = BRIDGE_DOC.read_text(encoding="utf-8")

    assert "Phase 12" in text
    assert "Documentation hardening, archive readiness, and final non-production delivery package" in text
    assert "文档硬化、归档准备与最终 non-production 交付包" in text

    for day in ["P12-D1", "P12-D2", "P12-D3", "P12-D4", "P12-D5", "P12-D6", "P12-D7", "P12-D8"]:
        assert day in text


def test_p11_to_p12_bridge_doc_mentions_phase12_candidate_directions():
    text = BRIDGE_DOC.read_text(encoding="utf-8")

    for item in [
        "documentation hardening plan",
        "final non-production delivery package",
        "archive readiness checklist",
        "final command index",
        "final artifact manifest",
        "final safety boundary declaration",
        "final operator delivery note",
        "Phase 12 acceptance smoke",
    ]:
        assert item in text


def test_p11_to_p12_bridge_doc_keeps_safety_boundaries():
    text = BRIDGE_DOC.read_text(encoding="utf-8")

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


def test_p11_to_p12_bridge_package_summary_still_ready_for_bridge():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["package_summary"]["ready_for_p11_d10_bridge_plan"] is True
    assert result["package_summary"]["p11_acceptance_completed"] is True
    assert result["package_summary"]["regression_stability_gate_ok"] is True
    assert result["package_summary"]["deliverables_all_present"] is True
    assert result["package_summary"]["safe_boundary_ok"] is True
