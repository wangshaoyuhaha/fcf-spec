from scripts.run_portfolio_guarded_paper_execution_smoke import run_smoke


def test_portfolio_guarded_paper_execution_smoke_completes():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["runner"] == "portfolio_guarded_paper_execution_smoke"
    assert result["fixture_path"] == "fixtures/paper_order_portfolios_multi_asset.json"
    assert result["portfolio_case_count"] == 4
    assert result["passed_count"] == 4
    assert result["failed_count"] == 0


def test_portfolio_guarded_paper_execution_smoke_branch_counts():
    result = run_smoke()

    assert result["portfolio_branch_counts"] == {
        "portfolio_all_fill": 1,
        "portfolio_mixed_results": 1,
        "portfolio_policy_deny": 1,
        "portfolio_risk_deny": 1,
    }


def test_portfolio_guarded_paper_execution_smoke_response_type_counts():
    result = run_smoke()

    assert result["response_type_counts"] == {
        "portfolio_paper_partial_success": 1,
        "portfolio_paper_success": 1,
        "portfolio_policy_deny": 1,
        "portfolio_risk_deny": 1,
    }


def test_portfolio_guarded_paper_execution_smoke_cases_pass():
    result = run_smoke()

    for case in result["cases"]:
        assert case["passed"] is True
        assert case["response_type"] == case["expected_response_type"]
        assert case["checks"]["no_real_execution_claim"] is True
        assert case["checks"]["safety_notice_present"] is True


def test_portfolio_guarded_paper_execution_smoke_expected_statuses():
    result = run_smoke()
    cases = {case["case_id"]: case for case in result["cases"]}

    assert cases["portfolio_all_fill"]["api_ok"] is True
    assert cases["portfolio_all_fill"]["portfolio_status"] == "completed"
    assert cases["portfolio_all_fill"]["filled_count"] == 4

    assert cases["portfolio_mixed_results"]["api_ok"] is True
    assert cases["portfolio_mixed_results"]["portfolio_status"] == "partial"
    assert cases["portfolio_mixed_results"]["filled_count"] == 1
    assert cases["portfolio_mixed_results"]["sandbox_rejected_count"] == 1
    assert cases["portfolio_mixed_results"]["policy_denied_count"] == 1
    assert cases["portfolio_mixed_results"]["risk_denied_count"] == 1

    assert cases["portfolio_policy_deny"]["api_ok"] is False
    assert cases["portfolio_policy_deny"]["error_type"] == "PortfolioPolicyDeny"

    assert cases["portfolio_risk_deny"]["api_ok"] is False
    assert cases["portfolio_risk_deny"]["error_type"] == "PortfolioRiskDeny"


def test_portfolio_guarded_paper_execution_smoke_safe_boundary():
    result = run_smoke()
    boundary = result["safe_boundary"]

    assert boundary["execution_mode"] == "paper"
    assert boundary["real_order"] is False
    assert boundary["real_execution"] is False
    assert boundary["real_exchange_api"] is False
    assert boundary["real_money_impact"] is False
    assert boundary["no_real_exchange_api"] is True
    assert boundary["no_real_order_placement"] is True
    assert boundary["no_exchange_api_key_storage"] is True
    assert boundary["no_wallet_private_key_access"] is True
    assert boundary["no_real_account_balance_read"] is True
    assert boundary["no_real_position_read"] is True
    assert boundary["does_not_claim_real_trade_success"] is True
