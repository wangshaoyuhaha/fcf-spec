from fcf.api.dify_http_adapter import (
    ROUTE_BATCH,
    ROUTE_CONTRACT,
    ROUTE_SINGLE,
    describe_routes,
    route_dify_http_request,
)


def _sample_raw_market_data():
    return {
        "asset_class": "crypto",
        "symbol": "BTCUSDT",
        "venue": "binance",
        "market_type": "perp",
        "timestamp": "2026-06-30T00:00:00Z",
        "timeframe": "1m",
        "source": "unit_test_dify_http_adapter",
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


def _sample_batch_rows():
    btc = _sample_raw_market_data()
    eth = _sample_raw_market_data()
    eth["symbol"] = "ETHUSDT"
    eth["market_type"] = "spot"
    eth["open"] = "3300"
    eth["high"] = "3310"
    eth["low"] = "3290"
    eth["close"] = "3305"
    eth["last_price"] = "3305"
    eth["volume"] = "900.25"
    eth["quote_volume"] = "2975626.25"
    eth["best_bid"] = "3304.9"
    eth["best_ask"] = "3305.1"
    eth["bid_depth"] = "500"
    eth["ask_depth"] = "450"
    return [btc, eth]


def test_describe_routes_declares_safe_boundary():
    routes = describe_routes()

    assert routes["api"] == "dify_http_adapter"
    assert "GET /api/v1/contract" in routes["routes"]
    assert "POST /api/v1/market-input/single" in routes["routes"]
    assert "POST /api/v1/market-input/batch" in routes["routes"]
    assert routes["safe_boundary"]["no_real_exchange_api"] is True
    assert routes["safe_boundary"]["no_real_order_placement"] is True
    assert routes["safe_boundary"]["only_calls_controlled_wrappers"] is True


def test_contract_route_returns_contract():
    response = route_dify_http_request("GET", ROUTE_CONTRACT)

    assert response["http_status"] == 200
    assert response["body"]["ok"] is True
    assert response["body"]["api"] == "dify_http_adapter"
    assert response["body"]["data"]["api"] == "local_market_input_api"
    assert "no real order placement" in response["body"]["data"]["forbidden_actions"]


def test_single_route_returns_success_response(tmp_path):
    response = route_dify_http_request(
        "POST",
        ROUTE_SINGLE,
        {
            "correlation_id": "p3-d9-single",
            "output_path": str(tmp_path / "single.jsonl"),
            "raw": _sample_raw_market_data(),
        },
    )

    assert response["http_status"] == 200
    assert response["body"]["ok"] is True
    assert response["body"]["api"] == "local_market_input_api"
    assert response["body"]["data"]["status"] == "completed"
    assert response["body"]["data"]["symbol"] == "BTCUSDT"
    assert response["body"]["data"]["event_count"] == 1
    assert response["body"]["data"]["replay"]["status"] == "completed"


def test_batch_route_returns_success_response(tmp_path):
    response = route_dify_http_request(
        "POST",
        ROUTE_BATCH,
        {
            "correlation_id": "p3-d9-batch",
            "output_path": str(tmp_path / "batch.jsonl"),
            "rows": _sample_batch_rows(),
        },
    )

    assert response["http_status"] == 200
    assert response["body"]["ok"] is True
    assert response["body"]["api"] == "local_market_input_api"
    assert response["body"]["data"]["event_count"] == 2
    assert response["body"]["data"]["symbols"] == ["BTCUSDT", "ETHUSDT"]
    assert response["body"]["data"]["replay"]["event_count"] == 2


def test_wrapper_validation_error_maps_to_422():
    raw = _sample_raw_market_data()
    raw["last_price"] = "bad-number"

    response = route_dify_http_request(
        "POST",
        ROUTE_SINGLE,
        {
            "correlation_id": "p3-d9-validation-error",
            "raw": raw,
        },
    )

    assert response["http_status"] == 422
    assert response["body"]["ok"] is False
    assert response["body"]["api"] == "local_market_input_api"
    assert response["body"]["error"]["type"] == "ValueError"
    assert "last_price" in response["body"]["error"]["message"]


def test_missing_request_fields_return_400():
    response = route_dify_http_request(
        "POST",
        ROUTE_SINGLE,
        {
            "correlation_id": "p3-d9-missing-raw",
        },
    )

    assert response["http_status"] == 400
    assert response["body"]["ok"] is False
    assert response["body"]["api"] == "dify_http_adapter"
    assert response["body"]["error"]["type"] == "BadRequest"
    assert "raw" in response["body"]["error"]["message"]


def test_unknown_route_and_wrong_method_are_rejected():
    unknown = route_dify_http_request("POST", "/api/v1/not-real", {})
    wrong_method = route_dify_http_request("GET", ROUTE_SINGLE, {})

    assert unknown["http_status"] == 404
    assert unknown["body"]["error"]["type"] == "NotFound"

    assert wrong_method["http_status"] == 405
    assert wrong_method["body"]["error"]["type"] == "MethodNotAllowed"
