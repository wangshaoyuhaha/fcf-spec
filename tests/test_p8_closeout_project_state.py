from pathlib import Path

from scripts.run_portfolio_guarded_paper_execution_smoke import run_smoke


CLOSEOUT_DOC = Path("docs/77_p8_closeout_project_state.md")


def test_p8_closeout_doc_exists():
    assert CLOSEOUT_DOC.exists()


def test_p8_closeout_doc_mentions_p8_days_and_artifacts():
    text = CLOSEOUT_DOC.read_text(encoding="utf-8")

    for day in ["P8-D1", "P8-D2", "P8-D3", "P8-D4", "P8-D5", "P8-D6", "P8-D7", "P8-D8"]:
        assert day in text

    for artifact in [
        "fixtures/paper_order_portfolios_multi_asset.json",
        "fcf/api/portfolio_paper_execution_api.py",
        "fcf/policy/portfolio_risk_guardian.py",
        "fcf/api/portfolio_paper_execution_response_templates.py",
        "scripts/run_portfolio_guarded_paper_execution_smoke.py",
    ]:
        assert artifact in text


def test_p8_closeout_doc_mentions_cases_and_response_types():
    text = CLOSEOUT_DOC.read_text(encoding="utf-8")

    for case_id in [
        "portfolio_all_fill",
        "portfolio_mixed_results",
        "portfolio_policy_deny",
        "portfolio_risk_deny",
    ]:
        assert case_id in text

    for response_type in [
        "portfolio_paper_success",
        "portfolio_paper_partial_success",
        "portfolio_policy_deny",
        "portfolio_risk_deny",
        "portfolio_schema_error",
    ]:
        assert response_type in text


def test_p8_closeout_doc_mentions_risk_rules():
    text = CLOSEOUT_DOC.read_text(encoding="utf-8")

    for rule in [
        "max_order_count",
        "max_total_notional",
        "max_asset_class_notional",
        "blocked_asset_classes",
        "blocked_symbols",
        "duplicate_order_keys",
        "max_same_side_count",
        "max_single_order_notional",
    ]:
        assert rule in text


def test_p8_closeout_smoke_still_completes():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["portfolio_case_count"] == 4
    assert result["passed_count"] == 4
    assert result["failed_count"] == 0
    assert result["response_type_counts"] == {
        "portfolio_paper_partial_success": 1,
        "portfolio_paper_success": 1,
        "portfolio_policy_deny": 1,
        "portfolio_risk_deny": 1,
    }


def test_p8_closeout_doc_keeps_safety_boundaries():
    text = CLOSEOUT_DOC.read_text(encoding="utf-8")

    assert "不接真实交易所 API" in text
    assert "不保存真实 API key" in text
    assert "不读取钱包私钥" in text
    assert "不真实下单" in text
    assert "不读取真实账户余额" in text
    assert "不读取真实仓位" in text
    assert "不声明真实成交" in text
    assert "不声明真实资金影响" in text
    assert "不把 paper execution 伪装成 real execution" in text
