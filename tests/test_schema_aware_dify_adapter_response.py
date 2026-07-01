from fcf.api.dify_http_adapter import ROUTE_SINGLE, route_dify_http_request
from fcf.api.dify_response_templates import render_dify_user_response


def _sample_raw_market_data():
    return {
        "asset_class": "Crypto",
        "symbol": "btcusdt",
        "venue": "BINANCE",
        "market_type": "PERP",
        "timestamp": "2026-06-30T00:00:00Z",
        "timeframe": "1m",
        "source": "unit_test_schema_aware_dify",
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


def _call_single(raw):
    return route_dify_http_request(
        "POST",
        ROUTE_SINGLE,
        {
            "correlation_id": "p4-d4-schema-aware",
            "raw": raw,
        },
    )


def _assert_schema_error_response(response, expected_text):
    assert response["http_status"] == 422
    assert response["body"]["ok"] is False
    assert response["body"]["api"] == "local_market_input_api"
    assert response["body"]["error"]["type"] == "ValueError"
    assert expected_text in response["body"]["error"]["message"]

    user_response = render_dify_user_response(response)

    assert user_response["ok"] is True
    assert user_response["response_type"] == "error"
    assert user_response["title"] == "市场输入校验失败"
    assert user_response["fields"]["error_type"] == "ValueError"
    assert expected_text in user_response["fields"]["error_message"]
    assert "没有真实下单" in user_response["safety_notice"]


def test_dify_adapter_success_response_exposes_schema_summary():
    response = _call_single(_sample_raw_market_data())

    assert response["http_status"] == 200
    assert response["body"]["ok"] is True

    data = response["body"]["data"]

    assert data["schema"] == "raw_market_input_schema"
    assert data["schema_version"] == "0.1.0"
    assert data["asset_class"] == "crypto"
    assert data["symbol"] == "BTCUSDT"
    assert data["venue"] == "binance"
    assert data["market_type"] == "perpetual"
    assert data["timeframe"] == "1m"
    assert data["event_name"] == "fcf.market.raw_received"
    assert data["event_names"] == ["fcf.market.raw_received"]


def test_dify_adapter_missing_required_field_returns_422_and_user_error():
    raw = _sample_raw_market_data()
    del raw["last_price"]

    response = _call_single(raw)

    _assert_schema_error_response(response, "last_price")


def test_dify_adapter_bad_market_type_returns_422_and_user_error():
    raw = _sample_raw_market_data()
    raw["market_type"] = "not-real"

    response = _call_single(raw)

    _assert_schema_error_response(response, "market_type")


def test_dify_adapter_bad_spread_returns_422_and_user_error():
    raw = _sample_raw_market_data()
    raw["best_bid"] = "60060"
    raw["best_ask"] = "60050"

    response = _call_single(raw)

    _assert_schema_error_response(response, "best_bid")


def test_dify_adapter_bad_asset_class_returns_422_and_user_error():
    raw = _sample_raw_market_data()
    raw["asset_class"] = "not-real"

    response = _call_single(raw)

    _assert_schema_error_response(response, "asset_class")
