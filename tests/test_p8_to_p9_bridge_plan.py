from pathlib import Path

from scripts.run_p8_portfolio_guarded_paper_regression_summary import run_smoke


BRIDGE_DOC = Path("docs/79_p8_to_p9_bridge_plan.md")


def test_p8_to_p9_bridge_doc_exists():
    assert BRIDGE_DOC.exists()


def test_p8_to_p9_bridge_doc_mentions_p8_days():
    text = BRIDGE_DOC.read_text(encoding="utf-8")

    for day in [
        "P8-D1",
        "P8-D2",
        "P8-D3",
        "P8-D4",
        "P8-D5",
        "P8-D6",
        "P8-D7",
        "P8-D8",
        "P8-D9",
        "P8-D10",
    ]:
        assert day in text


def test_p8_to_p9_bridge_doc_mentions_phase9_theme_and_route():
    text = BRIDGE_DOC.read_text(encoding="utf-8")

    assert "Phase 9" in text
    assert "Global paper-only regression suite and CI-safe operational readiness" in text
    assert "全局 paper-only 回归套件与 CI 安全运行准备" in text

    for day in ["P9-D1", "P9-D2", "P9-D3", "P9-D4", "P9-D5", "P9-D6", "P9-D7", "P9-D8"]:
        assert day in text


def test_p8_to_p9_bridge_doc_mentions_phase9_candidate_directions():
    text = BRIDGE_DOC.read_text(encoding="utf-8")

    for item in [
        "统一 smoke / regression 入口",
        "P7 regression summary",
        "P8 portfolio regression summary",
        "全局 safe_boundary 校验",
        "machine-readable regression report",
        "CI-safe entrypoint",
        "项目状态一致性检查",
    ]:
        assert item in text


def test_p8_to_p9_bridge_doc_keeps_safety_boundaries():
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
        "不把 paper execution 伪装成 real execution",
        "CI secret 配置",
        "production deployment",
    ]:
        assert item in text


def test_p8_to_p9_bridge_regression_still_ready_for_phase9():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["regression_summary"]["ready_for_phase9_planning"] is True
    assert result["regression_summary"]["p7_regression_completed"] is True
    assert result["regression_summary"]["p8_portfolio_smoke_completed"] is True
    assert result["regression_summary"]["p8_portfolio_case_count"] == 4
    assert result["regression_summary"]["p8_portfolio_failed_count"] == 0
