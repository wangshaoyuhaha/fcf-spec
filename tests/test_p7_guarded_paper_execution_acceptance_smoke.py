from scripts.run_p7_guarded_paper_execution_acceptance_smoke import run_smoke


def test_p7_guarded_paper_execution_acceptance_smoke_completes():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["runner"] == "p7_guarded_paper_execution_acceptance_smoke"


def test_p7_guarded_paper_execution_acceptance_smoke_artifacts_present():
    result = run_smoke()
    artifact_checks = result["artifact_checks"]

    assert artifact_checks["all_present"] is True
    assert artifact_checks["artifact_count"] == 12
    assert artifact_checks["missing"] == []

    for exists in artifact_checks["checks"].values():
        assert exists is True


def test_p7_guarded_paper_execution_acceptance_smoke_summary():
    result = run_smoke()
    summary = result["acceptance_summary"]

    assert summary["p7_d2_fixture_complete"] is True
    assert summary["p7_d3_execution_smoke_complete"] is True
    assert summary["p7_d4_response_smoke_complete"] is True
    assert summary["p7_d5_acceptance_doc_complete"] is True
    assert summary["case_count"] == 16
    assert summary["asset_class_count"] == 4
    assert summary["branch_count"] == 4
    assert summary["response_type_count"] == 4
    assert summary["expected_asset_class_counts_match"] is True
    assert summary["expected_branch_counts_match"] is True
    assert summary["expected_response_type_counts_match"] is True
    assert summary["all_execution_cases_passed"] is True
    assert summary["all_response_cases_passed"] is True


def test_p7_guarded_paper_execution_acceptance_smoke_execution_and_response_summaries():
    result = run_smoke()

    execution = result["execution_smoke_summary"]
    response = result["response_smoke_summary"]

    assert execution["status"] == "completed"
    assert execution["case_count"] == 16
    assert execution["passed_count"] == 16
    assert execution["failed_count"] == 0
    assert execution["asset_class_counts"] == {
        "commodities": 4,
        "crypto": 4,
        "equities": 4,
        "fx": 4,
    }
    assert execution["branch_counts"] == {
        "fill_success": 4,
        "policy_deny": 4,
        "risk_deny": 4,
        "sandbox_reject": 4,
    }

    assert response["status"] == "completed"
    assert response["case_count"] == 16
    assert response["passed_count"] == 16
    assert response["failed_count"] == 0
    assert response["response_type_counts"] == {
        "paper_fill_success": 4,
        "paper_policy_deny": 4,
        "paper_reject_success": 4,
        "paper_risk_deny": 4,
    }


def test_p7_guarded_paper_execution_acceptance_smoke_safe_boundary():
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
    assert boundary["policy_risk_cannot_be_bypassed"] is True
    assert boundary["does_not_claim_real_trade_success"] is True
    assert boundary["sandbox_fill_is_not_real_fill"] is True
    assert boundary["sandbox_reject_is_not_exchange_reject"] is True
    assert boundary["policy_deny_is_not_exchange_reject"] is True
    assert boundary["risk_deny_is_not_exchange_reject"] is True
