from pathlib import Path

from scripts.run_p8_portfolio_guarded_paper_regression_summary import run_smoke


PLAN_DOC = Path("docs/80_p9_global_regression_suite_plan.md")


def test_p9_global_regression_suite_plan_doc_exists():
    assert PLAN_DOC.exists()


def test_p9_global_regression_suite_plan_mentions_phase9_theme():
    text = PLAN_DOC.read_text(encoding="utf-8")

    assert "P9-D1" in text
    assert "Phase 9" in text
    assert "Global paper-only regression suite and CI-safe operational readiness" in text
    assert "全局 paper-only 回归套件与 CI 安全运行准备" in text


def test_p9_global_regression_suite_plan_mentions_core_targets():
    text = PLAN_DOC.read_text(encoding="utf-8")

    for item in [
        "统一 smoke / regression 入口",
        "P7 regression summary",
        "P8 portfolio regression summary",
        "machine-readable regression report",
        "全局 safe_boundary checker",
        "PROJECT_STATE / README consistency checker",
        "CI-safe regression command document",
    ]:
        assert item in text


def test_p9_global_regression_suite_plan_mentions_entrypoints_and_report():
    text = PLAN_DOC.read_text(encoding="utf-8")

    assert "scripts/run_all_smokes.py" in text
    assert "scripts/run_regression_suite.py" in text

    for item in [
        "report_version",
        "generated_by",
        "suites",
        "counts",
        "safe_boundary",
        "readiness",
        "next_action",
    ]:
        assert item in text


def test_p9_global_regression_suite_plan_mentions_p9_route_and_safety():
    text = PLAN_DOC.read_text(encoding="utf-8")

    for day in ["P9-D1", "P9-D2", "P9-D3", "P9-D4", "P9-D5", "P9-D6", "P9-D7", "P9-D8"]:
        assert day in text

    for item in [
        "不接真实交易所 API",
        "不保存真实 API key",
        "不读取钱包私钥",
        "不真实下单",
        "不读取真实账户余额",
        "不读取真实仓位",
        "不声明真实成交",
        "不声明真实资金影响",
        "CI secret 配置",
        "production deployment",
    ]:
        assert item in text


def test_p9_global_regression_suite_plan_p8_regression_still_ready():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["regression_summary"]["ready_for_phase9_planning"] is True
    assert result["regression_summary"]["p7_regression_completed"] is True
    assert result["regression_summary"]["p8_portfolio_smoke_completed"] is True
    assert result["regression_summary"]["p8_portfolio_failed_count"] == 0
