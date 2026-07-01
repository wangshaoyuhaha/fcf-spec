from pathlib import Path

from scripts.run_p10_dify_safe_package_summary import run_smoke


BRIDGE_DOC = Path("docs/99_p10_to_p11_bridge_plan.md")


def test_p10_to_p11_bridge_doc_exists():
    assert BRIDGE_DOC.exists()


def test_p10_to_p11_bridge_doc_mentions_p10_days():
    text = BRIDGE_DOC.read_text(encoding="utf-8")

    for day in [
        "P10-D1",
        "P10-D2",
        "P10-D3",
        "P10-D4",
        "P10-D5",
        "P10-D6",
        "P10-D7",
        "P10-D8",
        "P10-D9",
        "P10-D10",
    ]:
        assert day in text


def test_p10_to_p11_bridge_doc_mentions_phase11_theme_and_route():
    text = BRIDGE_DOC.read_text(encoding="utf-8")

    assert "Phase 11" in text
    assert "Release readiness, operator handoff package, and long-term maintainability" in text
    assert "发布准备、人工操作交接包与长期可维护性" in text

    for day in ["P11-D1", "P11-D2", "P11-D3", "P11-D4", "P11-D5", "P11-D6", "P11-D7", "P11-D8"]:
        assert day in text


def test_p10_to_p11_bridge_doc_mentions_phase11_candidate_directions():
    text = BRIDGE_DOC.read_text(encoding="utf-8")

    for item in [
        "release readiness plan",
        "operator handoff package",
        "versioned run commands document",
        "artifact inventory",
        "maintenance checklist",
        "regression stability gate",
        "long-term safety boundary checklist",
        "Phase 11 acceptance smoke",
    ]:
        assert item in text


def test_p10_to_p11_bridge_doc_keeps_safety_boundaries():
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


def test_p10_to_p11_bridge_package_summary_still_ready_for_bridge():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["package_summary"]["ready_for_p10_d10_bridge_plan"] is True
    assert result["package_summary"]["p10_acceptance_completed"] is True
    assert result["package_summary"]["dify_global_regression_ok"] is True
    assert result["package_summary"]["operator_response_passed"] is True
    assert result["package_summary"]["deliverables_all_present"] is True
    assert result["package_summary"]["safe_boundary_ok"] is True
