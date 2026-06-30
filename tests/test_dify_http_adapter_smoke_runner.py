from scripts.run_dify_http_adapter_smoke import run_smoke


def test_dify_http_adapter_smoke_runner_completes():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["runner"] == "dify_http_adapter_smoke"
    assert result["case_count"] == 5
    assert result["safe_boundary"]["no_real_exchange_api"] is True
    assert result["safe_boundary"]["no_real_order_placement"] is True
    assert result["safe_boundary"]["only_calls_controlled_wrappers"] is True


def test_dify_http_adapter_smoke_runner_cases_are_stable():
    result = run_smoke()
    cases = {case["name"]: case for case in result["cases"]}

    assert cases["contract"]["http_status"] == 200
    assert cases["contract"]["ok"] is True

    assert cases["single_success"]["http_status"] == 200
    assert cases["single_success"]["ok"] is True

    assert cases["batch_success"]["http_status"] == 200
    assert cases["batch_success"]["ok"] is True

    assert cases["single_bad_input"]["http_status"] == 422
    assert cases["single_bad_input"]["ok"] is False
    assert cases["single_bad_input"]["error_type"] == "ValueError"

    assert cases["unknown_route"]["http_status"] == 404
    assert cases["unknown_route"]["ok"] is False
    assert cases["unknown_route"]["error_type"] == "NotFound"
