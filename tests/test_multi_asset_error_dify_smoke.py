from scripts.run_multi_asset_error_dify_smoke import (
    load_multi_asset_fixture,
    run_multi_asset_error_dify_smoke,
)


def test_multi_asset_error_fixture_loads_from_good_fixture():
    rows = load_multi_asset_fixture()

    assert len(rows) == 4
    assert [row["asset_class"] for row in rows] == [
        "crypto",
        "equities",
        "fx",
        "commodities",
    ]


def test_multi_asset_error_dify_smoke_completes_and_is_safe():
    result = run_multi_asset_error_dify_smoke()

    assert result["status"] == "completed"
    assert result["runner"] == "multi_asset_error_dify_smoke"
    assert result["fixture_path"] == "fixtures/raw_market_data_multi_asset.json"
    assert result["case_count"] == 3
    assert result["safe_boundary"]["no_real_exchange_api"] is True
    assert result["safe_boundary"]["no_real_order_placement"] is True
    assert result["safe_boundary"]["only_calls_controlled_wrappers"] is True
    assert result["safe_boundary"]["does_not_claim_real_trade_success"] is True


def test_multi_asset_error_cases_return_422_and_adapter_errors():
    result = run_multi_asset_error_dify_smoke()
    cases = {case["name"]: case for case in result["cases"]}

    equities = cases["equities_bad_market_type"]
    assert equities["adapter_http_status"] == 422
    assert equities["adapter_ok"] is False
    assert equities["adapter_error_type"] == "ValueError"
    assert "market_type" in equities["adapter_error_message"]

    fx = cases["fx_bad_spread"]
    assert fx["adapter_http_status"] == 422
    assert fx["adapter_ok"] is False
    assert fx["adapter_error_type"] == "ValueError"
    assert "best_bid" in fx["adapter_error_message"]

    commodities = cases["commodities_missing_last_price"]
    assert commodities["adapter_http_status"] == 422
    assert commodities["adapter_ok"] is False
    assert commodities["adapter_error_type"] == "ValueError"
    assert "last_price" in commodities["adapter_error_message"]


def test_multi_asset_error_cases_render_user_error_responses():
    result = run_multi_asset_error_dify_smoke()

    for case in result["cases"]:
        assert case["user_response_type"] == "error"
        assert case["user_title"] == "市场输入校验失败"
        assert case["user_error_type"] == "ValueError"
        assert case["expected_text"] in case["user_error_message"]
