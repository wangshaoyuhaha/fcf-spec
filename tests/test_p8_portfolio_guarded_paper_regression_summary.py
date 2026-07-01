from scripts.run_p8_portfolio_guarded_paper_regression_summary import run_smoke


def test_p8_portfolio_regression_summary_completes():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["runner"] == "p8_portfolio_guarded_paper_regression_summary"


def test_p8_portfolio_regression_summary_fields():
    result = run_smoke()
    summary = result["regression_summary"]

    assert summary["phase"] == "P8"
    assert summary["phase_name"] == "portfolio guarded paper execution"
    assert summary["post_closeout_regression"] is True
    assert summary["p7_regression_completed"] is True
    assert summary["p8_portfolio_smoke_completed"] is True
    assert summary["ready_for_phase9_planning"] is True


def test_p8_portfolio_regression_summary_counts():
    result = run_smoke()
    summary = result["regression_summary"]

    assert summary["p8_portfolio_case_count"] == 4
    assert summary["p8_portfolio_passed_count"] == 4
    assert summary["p8_portfolio_failed_count"] == 0
    assert summary["p8_portfolio_branch_count"] == 4
    assert summary["p8_response_type_count"] == 4


def test_p8_portfolio_regression_summary_p8_details():
    result = run_smoke()
    p8 = result["p8_portfolio_summary"]

    assert p8["status"] == "completed"
    assert p8["portfolio_branch_counts"] == {
        "portfolio_all_fill": 1,
        "portfolio_mixed_results": 1,
        "portfolio_policy_deny": 1,
        "portfolio_risk_deny": 1,
    }
    assert p8["response_type_counts"] == {
        "portfolio_paper_partial_success": 1,
        "portfolio_paper_success": 1,
        "portfolio_policy_deny": 1,
        "portfolio_risk_deny": 1,
    }


def test_p8_portfolio_regression_summary_p7_details_present():
    result = run_smoke()
    p7 = result["p7_regression_summary"]

    assert p7["phase"] == "P7"
    assert p7["all_smokes_completed"] is True
    assert p7["ready_for_phase8_planning"] is True


def test_p8_portfolio_regression_summary_safe_boundary():
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
