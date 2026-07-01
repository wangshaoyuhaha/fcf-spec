from scripts.run_p7_guarded_paper_execution_regression_summary import (
    SMOKE_SCRIPTS,
    run_smoke,
)


def test_p7_regression_summary_completes():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["runner"] == "p7_guarded_paper_execution_regression_summary"
    assert result["smoke_count"] == 9
    assert result["completed_count"] == 9
    assert result["failed_count"] == 0


def test_p7_regression_summary_runs_expected_smoke_scripts():
    result = run_smoke()
    scripts = [item["script"] for item in result["smoke_results"]]

    assert scripts == SMOKE_SCRIPTS

    for item in result["smoke_results"]:
        assert item["returncode"] == 0
        assert item["stdout_json_parse_ok"] is True
        assert item["status"] == "completed"
        assert item["stderr"] == ""


def test_p7_regression_summary_guarded_execution_counts():
    result = run_smoke()
    summary = result["guarded_summary"]

    assert summary["execution_case_count"] == 16
    assert summary["execution_passed_count"] == 16
    assert summary["execution_failed_count"] == 0
    assert summary["execution_asset_class_counts"] == {
        "commodities": 4,
        "crypto": 4,
        "equities": 4,
        "fx": 4,
    }
    assert summary["execution_branch_counts"] == {
        "fill_success": 4,
        "policy_deny": 4,
        "risk_deny": 4,
        "sandbox_reject": 4,
    }


def test_p7_regression_summary_guarded_response_counts():
    result = run_smoke()
    summary = result["guarded_summary"]

    assert summary["response_case_count"] == 16
    assert summary["response_passed_count"] == 16
    assert summary["response_failed_count"] == 0
    assert summary["response_type_counts"] == {
        "paper_fill_success": 4,
        "paper_policy_deny": 4,
        "paper_reject_success": 4,
        "paper_risk_deny": 4,
    }


def test_p7_regression_summary_acceptance_summary():
    result = run_smoke()
    acceptance = result["guarded_summary"]["acceptance_summary"]

    assert acceptance["p7_d2_fixture_complete"] is True
    assert acceptance["p7_d3_execution_smoke_complete"] is True
    assert acceptance["p7_d4_response_smoke_complete"] is True
    assert acceptance["p7_d5_acceptance_doc_complete"] is True
    assert acceptance["case_count"] == 16
    assert acceptance["asset_class_count"] == 4
    assert acceptance["branch_count"] == 4
    assert acceptance["response_type_count"] == 4
    assert acceptance["all_execution_cases_passed"] is True
    assert acceptance["all_response_cases_passed"] is True


def test_p7_regression_summary_regression_fields_and_safe_boundary():
    result = run_smoke()
    regression = result["regression_summary"]
    boundary = result["safe_boundary"]

    assert regression["phase"] == "P7"
    assert regression["phase_name"] == "guarded paper execution"
    assert regression["post_closeout_regression"] is True
    assert regression["smoke_count"] == 9
    assert regression["completed_count"] == 9
    assert regression["failed_count"] == 0
    assert regression["all_smokes_completed"] is True
    assert regression["guarded_execution_cases"] == 16
    assert regression["guarded_response_cases"] == 16
    assert regression["asset_class_count"] == 4
    assert regression["branch_count"] == 4
    assert regression["response_type_count"] == 4
    assert regression["ready_for_phase8_planning"] is True

    assert boundary["execution_mode"] == "paper"
    assert boundary["real_order"] is False
    assert boundary["real_execution"] is False
    assert boundary["real_exchange_api"] is False
    assert boundary["real_money_impact"] is False
    assert boundary["no_real_exchange_api"] is True
    assert boundary["no_real_order_placement"] is True
    assert boundary["no_exchange_api_key_storage"] is True
    assert boundary["no_wallet_private_key_access"] is True
    assert boundary["policy_risk_cannot_be_bypassed"] is True
    assert boundary["does_not_claim_real_trade_success"] is True
    assert boundary["sandbox_fill_is_not_real_fill"] is True
    assert boundary["sandbox_reject_is_not_exchange_reject"] is True
    assert boundary["policy_deny_is_not_exchange_reject"] is True
    assert boundary["risk_deny_is_not_exchange_reject"] is True
