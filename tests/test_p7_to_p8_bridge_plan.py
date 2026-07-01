from pathlib import Path

from scripts.run_p7_guarded_paper_execution_regression_summary import run_smoke


BRIDGE_DOC = Path("docs/69_p7_to_p8_bridge_plan.md")


def test_p7_to_p8_bridge_doc_exists():
    assert BRIDGE_DOC.exists()


def test_p7_to_p8_bridge_doc_mentions_phase7_days_and_phase8():
    text = BRIDGE_DOC.read_text(encoding="utf-8")

    for day in [
        "P7-D1",
        "P7-D2",
        "P7-D3",
        "P7-D4",
        "P7-D5",
        "P7-D6",
        "P7-D7",
        "P7-D8",
        "P7-D9",
    ]:
        assert day in text

    assert "Phase 8" in text
    assert "P8-D1" in text
    assert "Portfolio-level guarded paper execution" in text


def test_p7_to_p8_bridge_doc_mentions_assets_branches_and_response_types():
    text = BRIDGE_DOC.read_text(encoding="utf-8")

    for asset_class in ["crypto", "equities", "fx", "commodities"]:
        assert asset_class in text

    for branch in ["fill_success", "sandbox_reject", "policy_deny", "risk_deny"]:
        assert branch in text

    for response_type in [
        "paper_fill_success",
        "paper_reject_success",
        "paper_policy_deny",
        "paper_risk_deny",
    ]:
        assert response_type in text


def test_p7_to_p8_bridge_doc_mentions_phase8_candidate_directions():
    text = BRIDGE_DOC.read_text(encoding="utf-8")

    assert "portfolio-level guarded paper execution" in text
    assert "cross-asset exposure checks" in text
    assert "portfolio-level user-facing response" in text
    assert "regression CI entrypoint" in text
    assert "scripts/run_all_smokes.py" in text
    assert "scripts/run_regression_suite.py" in text


def test_p7_to_p8_bridge_doc_mentions_phase8_d1_to_d6_route():
    text = BRIDGE_DOC.read_text(encoding="utf-8")

    for day in ["P8-D1", "P8-D2", "P8-D3", "P8-D4", "P8-D5", "P8-D6"]:
        assert day in text

    assert "docs/70_p8_portfolio_guarded_paper_execution_plan.md" in text
    assert "fixtures/paper_order_portfolios_multi_asset.json" in text
    assert "portfolio_paper_execution_api.py" in text
    assert "portfolio_risk_guardian.py" in text
    assert "portfolio_paper_execution_response_templates.py" in text
    assert "run_portfolio_guarded_paper_execution_smoke.py" in text


def test_p7_to_p8_bridge_doc_keeps_safety_boundaries():
    text = BRIDGE_DOC.read_text(encoding="utf-8")

    assert "不接真实交易所 API" in text
    assert "不保存真实 API key" in text
    assert "不读取钱包私钥" in text
    assert "不真实下单" in text
    assert "没有真实成交" in text
    assert "没有真实资金影响" in text
    assert "不配置真实 CI secret" in text


def test_p7_to_p8_bridge_regression_summary_still_ready_for_phase8():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["regression_summary"]["ready_for_phase8_planning"] is True
    assert result["regression_summary"]["all_smokes_completed"] is True
    assert result["regression_summary"]["smoke_count"] == 9
    assert result["regression_summary"]["completed_count"] == 9
    assert result["regression_summary"]["failed_count"] == 0
