from scripts.run_multi_asset_guarded_paper_execution_response_smoke import run_smoke


def test_multi_asset_guarded_paper_execution_response_smoke_completes():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["runner"] == "multi_asset_guarded_paper_execution_response_smoke"
    assert result["fixture_path"] == "fixtures/paper_orders_multi_asset_guarded.json"
    assert result["case_count"] == 16
    assert result["passed_count"] == 16
    assert result["failed_count"] == 0


def test_multi_asset_guarded_paper_execution_response_smoke_asset_counts():
    result = run_smoke()

    assert result["asset_class_counts"] == {
        "commodities": 4,
        "crypto": 4,
        "equities": 4,
        "fx": 4,
    }


def test_multi_asset_guarded_paper_execution_response_smoke_branch_counts():
    result = run_smoke()

    assert result["branch_counts"] == {
        "fill_success": 4,
        "policy_deny": 4,
        "risk_deny": 4,
        "sandbox_reject": 4,
    }


def test_multi_asset_guarded_paper_execution_response_smoke_response_type_counts():
    result = run_smoke()

    assert result["response_type_counts"] == {
        "paper_fill_success": 4,
        "paper_policy_deny": 4,
        "paper_reject_success": 4,
        "paper_risk_deny": 4,
    }


def test_multi_asset_guarded_paper_execution_response_smoke_case_results_match_expected():
    result = run_smoke()

    for case in result["cases"]:
        assert case["passed"] is True
        assert case["user_response_type"] == case["expected_response_type"]
        assert case["sandbox_event_written"] is case["sandbox_event_expected"]

        if case["branch"] == "fill_success":
            assert case["adapter_http_status"] == 200
            assert case["adapter_ok"] is True
            assert case["adapter_execution_status"] == "filled"
            assert case["user_response_type"] == "paper_fill_success"

        if case["branch"] == "sandbox_reject":
            assert case["adapter_http_status"] == 200
            assert case["adapter_ok"] is True
            assert case["adapter_execution_status"] == "rejected"
            assert case["user_response_type"] == "paper_reject_success"

        if case["branch"] == "policy_deny":
            assert case["adapter_http_status"] == 422
            assert case["adapter_ok"] is False
            assert case["adapter_error_type"] == "PolicyDeny"
            assert case["user_response_type"] == "paper_policy_deny"

        if case["branch"] == "risk_deny":
            assert case["adapter_http_status"] == 422
            assert case["adapter_ok"] is False
            assert case["adapter_error_type"] == "RiskDeny"
            assert case["user_response_type"] == "paper_risk_deny"


def test_multi_asset_guarded_paper_execution_response_smoke_safe_boundary():
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
    assert boundary["only_calls_dify_paper_execution_adapter"] is True
    assert boundary["only_renders_paper_user_responses"] is True
    assert boundary["does_not_claim_real_trade_success"] is True
    assert boundary["does_not_claim_sandbox_reject_as_exchange_reject"] is True
    assert boundary["does_not_claim_policy_deny_as_exchange_reject"] is True
    assert boundary["does_not_claim_risk_deny_as_exchange_reject"] is True
