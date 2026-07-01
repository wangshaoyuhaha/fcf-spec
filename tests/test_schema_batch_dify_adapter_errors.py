from fcf.api.dify_http_adapter import ROUTE_BATCH, route_dify_http_request
from fcf.api.dify_response_templates import render_dify_user_response


def _btc_raw_market_data():
    return {
        "asset_class": "Crypto",
        "symbol": "btcusdt",
        "venue": "BINANCE",
        "market_type": "PERP",
        "timestamp": "2026-06-30T00:00:00Z",
        "timeframe": "1m",
        "source": "unit_test_schema_batch_dify",
        "source_type": "mock",
        "open": "60000",
        "high": "60100",
        "low": "59900",
        "close": "60050",
        "last_price": "60050",
        "volume": "120.5",
        "quote_volume": "7230000",
        "best_bid": "60049.5",
        "best_ask": "60050.5",
        "bid_depth": "100",
        "ask_depth": "80",
    }


def _eth_raw_market_data():
    row = _btc_raw_market_data()
    row["symbol"] = "ethusdt"
    row["market_type"] = "spot"
    row["open"] = "3300"
    row["high"] = "3310"
    row["low"] = "3290"
    row["close"] = "3305"
    row["last_price"] = "3305"
    row["volume"] = "900.25"
    row["quote_volume"] = "2975626.25"
    row["best_bid"] = "3304.9"
    row["best_ask"] = "3305.1"
    row["bid_depth"] = "500"
    row["ask_depth"] = "450"
    return row


def _call_batch(rows):
    return route_dify_http_request(
        "POST",
        ROUTE_BATCH,
        {
            "correlation_id": "p4-d7-schema-batch",
            "rows": rows,
        },
    )


def _assert_batch_schema_error(response, expected_text):
    assert response["http_status"] == 422
    assert response["body"]["ok"] is False
    assert response["body"]["api"] == "local_market_input_api"
    assert response["body"]["error"]["type"] == "ValueError"
    assert expected_text in response["body"]["error"]["message"]
    assert response["body"]["data"] is None

    user_response = render_dify_user_response(response)

    assert user_response["ok"] is True
    assert user_response["response_type"] == "error"
    assert user_response["title"] == "市场输入校验失败"
    assert user_response["fields"]["error_type"] == "ValueError"
    assert expected_text in user_response["fields"]["error_message"]
    assert "没有真实下单" in user_response["safety_notice"]


def test_dify_batch_success_uses_schema_normalization():
    response = _call_batch([_btc_raw_market_data(), _eth_raw_market_data()])

    assert response["http_status"] == 200
    assert response["body"]["ok"] is True

    data = response["body"]["data"]

    assert data["schema"] == "raw_market_input_schema"
    assert data["schema_version"] == "0.1.0"
    assert data["event_count"] == 2
    assert data["symbols"] == ["BTCUSDT", "ETHUSDT"]
    assert data["asset_classes"] == ["crypto", "crypto"]
    assert data["market_types"] == ["perpetual", "spot"]
    assert data["event_names"] == [
        "fcf.market.raw_received",
        "fcf.market.raw_received",
    ]


def test_dify_batch_missing_required_field_returns_422_and_user_error():
    good = _btc_raw_market_data()
    bad = _eth_raw_market_data()
    del bad["last_price"]

    response = _call_batch([good, bad])

    _assert_batch_schema_error(response, "last_price")


def test_dify_batch_bad_market_type_returns_422_and_user_error():
    good = _btc_raw_market_data()
    bad = _eth_raw_market_data()
    bad["market_type"] = "not-real"

    response = _call_batch([good, bad])

    _assert_batch_schema_error(response, "market_type")


def test_dify_batch_bad_spread_returns_422_and_user_error():
    good = _btc_raw_market_data()
    bad = _eth_raw_market_data()
    bad["best_bid"] = "3306"
    bad["best_ask"] = "3305"

    response = _call_batch([good, bad])

    _assert_batch_schema_error(response, "best_bid")


def test_dify_batch_bad_asset_class_returns_422_and_user_error():
    good = _btc_raw_market_data()
    bad = _eth_raw_market_data()
    bad["asset_class"] = "not-real"

    response = _call_batch([good, bad])

    _assert_batch_schema_error(response, "asset_class")


def test_dify_batch_bad_number_returns_422_and_user_error():
    good = _btc_raw_market_data()
    bad = _eth_raw_market_data()
    bad["volume"] = "bad-number"

    response = _call_batch([good, bad])

    _assert_batch_schema_error(response, "volume")
