from scripts.run_multi_asset_guarded_paper_execution_smoke import run_smoke


def test_multi_asset_guarded_paper_execution_smoke_runner_completes():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["runner"] == "multi_asset_guarded_paper_execution_smoke"
    assert result["fixture_path"] == "fixtures/paper_orders_multi_asset_guarded.json"
    assert result["case_count"] == 16
    assert result["passed_count"] == 16
    assert result["failed_count"] == 0


def test_multi_asset_guarded_paper_execution_smoke_runner_asset_counts():
    result = run_smoke()

    assert result["asset_class_counts"] == {
        "commodities": 4,
        "crypto": 4,
        "equities": 4,
        "fx": 4,
    }


def test_multi_asset_guarded_paper_execution_smoke_runner_branch_counts():
    result = run_smoke()

    assert result["branch_counts"] == {
        "fill_success": 4,
        "policy_deny": 4,
        "risk_deny": 4,
        "sandbox_reject": 4,
    }


def test_multi_asset_guarded_paper_execution_smoke_runner_case_results_match_expected():
    result = run_smoke()

    for case in result["cases"]:
        assert case["passed"] is True
        assert case["actual_ok"] is case["expected_ok"]
        assert case["actual_error_type"] == case["expected_error_type"]
        assert case["actual_execution_status"] == case["expected_execution_status"]
        assert case["sandbox_event_written"] is case["sandbox_event_expected"]


def test_multi_asset_guarded_paper_execution_smoke_runner_safe_boundary():
    result = run_smoke()
    boundary = result["safe_boundary"]

    assert boundary["no_real_exchange_api"] is True
    assert boundary["no_real_order_placement"] is True
    assert boundary["no_exchange_api_key_storage"] is True
    assert boundary["no_wallet_private_key_access"] is True
    assert boundary["paper_only"] is True
    assert boundary["policy_risk_cannot_be_bypassed"] is True
    assert boundary["sandbox_reject_is_not_exchange_reject"] is True
    assert boundary["policy_deny_is_not_exchange_reject"] is True
    assert boundary["risk_deny_is_not_exchange_reject"] is True
