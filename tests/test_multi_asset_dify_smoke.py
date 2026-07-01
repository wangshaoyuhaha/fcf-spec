from scripts.run_multi_asset_dify_smoke import (
    load_multi_asset_fixture,
    run_multi_asset_dify_smoke,
)


def test_load_multi_asset_fixture_returns_four_rows():
    rows = load_multi_asset_fixture()

    assert len(rows) == 4
    assert [row["asset_class"] for row in rows] == [
        "crypto",
        "equities",
        "fx",
        "commodities",
    ]
    assert [row["symbol"] for row in rows] == [
        "BTCUSDT",
        "AAPL",
        "EURUSD",
        "XAUUSD",
    ]


def test_multi_asset_dify_smoke_completes_with_success_response():
    result = run_multi_asset_dify_smoke()

    assert result["status"] == "completed"
    assert result["runner"] == "multi_asset_dify_response_smoke"
    assert result["adapter_http_status"] == 200
    assert result["adapter_ok"] is True
    assert result["event_count"] == 4
    assert result["replay_status"] == "completed"
    assert result["replay_event_count"] == 4
    assert result["user_response_type"] == "success"
    assert result["user_title"] == "市场输入处理完成"


def test_multi_asset_dify_smoke_summary_is_stable_and_safe():
    result = run_multi_asset_dify_smoke()

    assert result["fixture_path"] == "fixtures/raw_market_data_multi_asset.json"
    assert result["asset_classes"] == [
        "crypto",
        "equities",
        "fx",
        "commodities",
    ]
    assert result["symbols"] == [
        "BTCUSDT",
        "AAPL",
        "EURUSD",
        "XAUUSD",
    ]
    assert result["market_types"] == [
        "perpetual",
        "spot",
        "spot",
        "futures",
    ]
    assert result["safe_boundary"]["no_real_exchange_api"] is True
    assert result["safe_boundary"]["no_real_order_placement"] is True
    assert result["safe_boundary"]["only_calls_controlled_wrappers"] is True
    assert result["safe_boundary"]["does_not_claim_real_trade_success"] is True
