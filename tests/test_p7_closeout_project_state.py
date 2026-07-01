from pathlib import Path

from scripts.run_p7_guarded_paper_execution_acceptance_smoke import run_smoke


CLOSEOUT_DOC = Path("docs/67_p7_closeout_project_state.md")


def test_p7_closeout_doc_exists():
    assert CLOSEOUT_DOC.exists()


def test_p7_closeout_doc_mentions_phase7_days_and_artifacts():
    text = CLOSEOUT_DOC.read_text(encoding="utf-8")

    for day in ["P7-D1", "P7-D2", "P7-D3", "P7-D4", "P7-D5", "P7-D6", "P7-D7"]:
        assert day in text

    for artifact in [
        "docs/61_p7_multi_asset_guarded_paper_execution_fixture_plan.md",
        "fixtures/paper_orders_multi_asset_guarded.json",
        "scripts/run_multi_asset_guarded_paper_execution_smoke.py",
        "scripts/run_multi_asset_guarded_paper_execution_response_smoke.py",
        "scripts/run_p7_guarded_paper_execution_acceptance_smoke.py",
        "docs/67_p7_closeout_project_state.md",
    ]:
        assert artifact in text


def test_p7_closeout_doc_mentions_assets_branches_and_response_types():
    text = CLOSEOUT_DOC.read_text(encoding="utf-8")

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


def test_p7_closeout_acceptance_smoke_still_completes():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["acceptance_summary"]["case_count"] == 16
    assert result["acceptance_summary"]["asset_class_count"] == 4
    assert result["acceptance_summary"]["branch_count"] == 4
    assert result["acceptance_summary"]["response_type_count"] == 4
    assert result["acceptance_summary"]["all_execution_cases_passed"] is True
    assert result["acceptance_summary"]["all_response_cases_passed"] is True


def test_p7_closeout_doc_mentions_api_order_and_deny_behavior():
    text = CLOSEOUT_DOC.read_text(encoding="utf-8")

    assert "evaluate_paper_execution_policy" in text
    assert "evaluate_paper_execution_risk" in text
    assert "execute_sandbox_order_with_eventstore" in text
    assert "PolicyDeny 直接返回 ok=false" in text
    assert "RiskDeny 直接返回 ok=false" in text
    assert "PolicyDeny 不进入 sandbox execution" in text
    assert "RiskDeny 不进入 sandbox execution" in text
    assert "PolicyDeny 不生成 sandbox execution event" in text
    assert "RiskDeny 不生成 sandbox execution event" in text


def test_p7_closeout_doc_keeps_safety_boundaries():
    text = CLOSEOUT_DOC.read_text(encoding="utf-8")

    assert "不接真实交易所 API" in text
    assert "不保存真实 API key" in text
    assert "不读取钱包私钥" in text
    assert "不真实下单" in text
    assert "不允许绕过 policy / risk" in text
    assert "不把 paper execution 伪装成 real execution" in text
    assert "sandbox fill 不是真实成交" in text
    assert "sandbox reject 不是交易所真实拒单" in text
    assert "PolicyDeny 不是交易所真实拒单" in text
    assert "RiskDeny 不是交易所真实拒单" in text
