from pathlib import Path

from scripts.run_p9_global_regression_summary import run_smoke


BRIDGE_DOC = Path("docs/89_p9_to_p10_bridge_plan.md")


def test_p9_to_p10_bridge_doc_exists():
    assert BRIDGE_DOC.exists()


def test_p9_to_p10_bridge_doc_mentions_p9_days():
    text = BRIDGE_DOC.read_text(encoding="utf-8")

    for day in [
        "P9-D1",
        "P9-D2",
        "P9-D3",
        "P9-D4",
        "P9-D5",
        "P9-D6",
        "P9-D7",
        "P9-D8",
        "P9-D9",
        "P9-D10",
    ]:
        assert day in text


def test_p9_to_p10_bridge_doc_mentions_phase10_theme_and_route():
    text = BRIDGE_DOC.read_text(encoding="utf-8")

    assert "Phase 10" in text
    assert "Dify-safe paper operations packaging and operator review readiness" in text
    assert "Dify 安全纸面操作封装与人工复核准备" in text

    for day in ["P10-D1", "P10-D2", "P10-D3", "P10-D4", "P10-D5", "P10-D6", "P10-D7", "P10-D8"]:
        assert day in text


def test_p9_to_p10_bridge_doc_mentions_phase10_candidate_directions():
    text = BRIDGE_DOC.read_text(encoding="utf-8")

    for item in [
        "Dify-safe global regression adapter",
        "paper-only operator runbook",
        "response templates for global regression status",
        "operator review checklist",
        "failure triage guide",
        "Dify workflow node contract",
        "handoff package for non-production paper-only use",
        "Phase 10 acceptance smoke",
    ]:
        assert item in text


def test_p9_to_p10_bridge_doc_keeps_safety_boundaries():
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
        "不把 paper execution 伪装成 real execution",
        "自动实盘交易",
        "自动绕过人工复核",
        "绕过 policy / risk / safe_boundary",
    ]:
        assert item in text


def test_p9_to_p10_bridge_global_summary_still_ready_for_phase10():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["global_summary"]["ready_for_phase10_planning"] is True
    assert result["global_summary"]["run_all_smokes_completed"] is True
    assert result["global_summary"]["p9_acceptance_completed"] is True
    assert result["global_summary"]["global_safe_boundary_ok"] is True
    assert result["global_summary"]["project_state_consistency_ok"] is True
