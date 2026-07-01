from scripts.run_dify_paper_execution_smoke import run_dify_paper_execution_smoke


def test_dify_paper_execution_smoke_completes_and_is_safe():
    result = run_dify_paper_execution_smoke()

    assert result["status"] == "completed"
    assert result["runner"] == "dify_paper_execution_smoke"
    assert result["case_count"] == 6
    assert result["safe_boundary"]["execution_mode"] == "paper"
    assert result["safe_boundary"]["real_order"] is False
    assert result["safe_boundary"]["real_execution"] is False
    assert result["safe_boundary"]["no_real_exchange_api"] is True
    assert result["safe_boundary"]["no_real_order_placement"] is True


def test_dify_paper_execution_smoke_success_cases_are_stable():
    result = run_dify_paper_execution_smoke()
    cases = {case["name"]: case for case in result["cases"]}

    contract = cases["contract"]
    assert contract["http_status"] == 200
    assert contract["ok"] is True
    assert contract["api"] == "dify_paper_execution_adapter"

    fill = cases["simulated_fill"]
    assert fill["http_status"] == 200
    assert fill["ok"] is True
    assert fill["api"] == "paper_execution_api"
    assert fill["execution_status"] == "filled"
    assert fill["event_name"] == "fcf.sandbox.execution.filled"
    assert fill["event_count"] == 1
    assert fill["replay_status"] == "completed"
    assert fill["real_order"] is False
    assert fill["real_execution"] is False

    reject = cases["simulated_reject"]
    assert reject["http_status"] == 200
    assert reject["ok"] is True
    assert reject["api"] == "paper_execution_api"
    assert reject["execution_status"] == "rejected"
    assert reject["event_name"] == "fcf.sandbox.execution.rejected"
    assert reject["event_count"] == 1
    assert reject["real_order"] is False
    assert reject["real_execution"] is False


def test_dify_paper_execution_smoke_error_cases_are_stable():
    result = run_dify_paper_execution_smoke()
    cases = {case["name"]: case for case in result["cases"]}

    bad_order = cases["bad_order_error"]
    assert bad_order["http_status"] == 422
    assert bad_order["ok"] is False
    assert bad_order["api"] == "paper_execution_api"
    assert bad_order["error_type"] == "ValueError"
    assert "quantity" in bad_order["error_message"]

    bad_mode = cases["bad_simulation_mode_error"]
    assert bad_mode["http_status"] == 422
    assert bad_mode["ok"] is False
    assert bad_mode["api"] == "paper_execution_api"
    assert bad_mode["error_type"] == "ValueError"
    assert "simulation_mode" in bad_mode["error_message"]

    missing = cases["missing_raw_order_error"]
    assert missing["http_status"] == 400
    assert missing["ok"] is False
    assert missing["api"] == "dify_paper_execution_adapter"
    assert missing["error_type"] == "BadRequest"
    assert "raw_order" in missing["error_message"]


def test_dify_paper_execution_smoke_does_not_claim_real_execution():
    result = run_dify_paper_execution_smoke()

    for case in result["cases"]:
        assert "no real exchange API" in case["user_visible_safety"]
        assert "no real order placement" in case["user_visible_safety"]

    success_cases = [
        case for case in result["cases"] if case["name"] in {"simulated_fill", "simulated_reject"}
    ]

    for case in success_cases:
        assert case["real_order"] is False
        assert case["real_execution"] is False
        assert case["real_exchange_api"] is False
        assert case["real_money_impact"] is False
