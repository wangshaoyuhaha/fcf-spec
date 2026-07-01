from pathlib import Path

from scripts.run_p7_guarded_paper_execution_regression_summary import run_smoke


PLAN_DOC = Path("docs/70_p8_portfolio_guarded_paper_execution_plan.md")


def test_p8_portfolio_plan_doc_exists():
    assert PLAN_DOC.exists()


def test_p8_portfolio_plan_doc_mentions_phase8_and_portfolio_topic():
    text = PLAN_DOC.read_text(encoding="utf-8")

    assert "P8-D1" in text
    assert "Phase 8" in text
    assert "Portfolio-level guarded paper execution" in text
    assert "组合级 guarded paper execution" in text


def test_p8_portfolio_plan_doc_mentions_input_output_and_order_fields():
    text = PLAN_DOC.read_text(encoding="utf-8")

    for field in [
        "portfolio_id",
        "correlation_id",
        "orders",
        "portfolio_policy_context",
        "portfolio_risk_context",
        "asset_class",
        "symbol",
        "venue",
        "market_type",
        "side",
        "order_type",
        "quantity",
        "price",
    ]:
        assert field in text

    assert "filled_count" in text
    assert "sandbox_rejected_count" in text
    assert "policy_denied_count" in text
    assert "risk_denied_count" in text


def test_p8_portfolio_plan_doc_mentions_policy_risk_and_execution_order():
    text = PLAN_DOC.read_text(encoding="utf-8")

    assert "evaluate_paper_execution_policy" in text
    assert "evaluate_paper_execution_risk" in text
    assert "execute_sandbox_order_with_eventstore" in text
    assert "不允许任何一笔 order 绕过 policy / risk" in text

    for rule in [
        "禁止真实执行请求",
        "禁止绕过 risk 请求",
        "禁止保存 API key 请求",
        "禁止连接真实交易所请求",
        "max_order_count",
        "max_total_notional",
        "max_asset_class_notional",
        "blocked_asset_classes",
        "blocked_symbols",
    ]:
        assert rule in text


def test_p8_portfolio_plan_doc_mentions_cross_asset_exposure_and_responses():
    text = PLAN_DOC.read_text(encoding="utf-8")

    for item in [
        "Cross-asset exposure checks",
        "total_notional",
        "notional_by_asset_class",
        "order_count_by_asset_class",
        "side_count_by_asset_class",
        "duplicated_symbols",
        "portfolio_paper_success",
        "portfolio_paper_partial_success",
        "portfolio_policy_deny",
        "portfolio_risk_deny",
        "portfolio_schema_error",
    ]:
        assert item in text


def test_p8_portfolio_plan_doc_mentions_regression_and_route():
    text = PLAN_DOC.read_text(encoding="utf-8")

    assert "scripts/run_regression_suite.py" in text
    assert "scripts/run_all_smokes.py" in text

    for day in ["P8-D1", "P8-D2", "P8-D3", "P8-D4", "P8-D5", "P8-D6", "P8-D7", "P8-D8"]:
        assert day in text

    assert "fixtures/paper_order_portfolios_multi_asset.json" in text
    assert "tests/test_portfolio_paper_order_fixture.py" in text


def test_p8_portfolio_plan_doc_keeps_safety_boundaries():
    text = PLAN_DOC.read_text(encoding="utf-8")

    assert "不接真实交易所 API" in text
    assert "不保存真实 API key" in text
    assert "不读取钱包私钥" in text
    assert "不真实下单" in text
    assert "不接账户余额" in text
    assert "不接真实仓位" in text
    assert "没有真实成交" in text
    assert "没有真实资金影响" in text
    assert "当前不配置真实 CI secret" in text


def test_p8_portfolio_plan_p7_regression_still_completed():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["regression_summary"]["ready_for_phase8_planning"] is True
    assert result["regression_summary"]["all_smokes_completed"] is True
    assert result["regression_summary"]["smoke_count"] == 9
    assert result["regression_summary"]["completed_count"] == 9
    assert result["regression_summary"]["failed_count"] == 0
