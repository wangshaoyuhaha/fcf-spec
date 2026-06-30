import json
from pathlib import Path

from fcf.api.local_market_input_api import (
    API_NAME,
    API_VERSION,
    describe_api_contract,
    handle_batch_market_input,
    handle_single_market_input,
)


def _sample_raw_market_data():
    return {
        "asset_class": "crypto",
        "symbol": "BTCUSDT",
        "venue": "binance",
        "market_type": "perp",
        "timestamp": "2026-06-30T00:00:00Z",
        "timeframe": "1m",
        "source": "unit_test_local_api",
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


def _fixture_rows():
    fixture_path = Path("fixtures/raw_market_data_crypto.json")
    with fixture_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_describe_api_contract_declares_boundaries():
    contract = describe_api_contract()

    assert contract["api"] == API_NAME
    assert contract["api_version"] == API_VERSION
    assert "Dify workflow" in contract["external_systems"]
    assert "validate raw market input" in contract["allowed_actions"]
    assert "no real exchange API key" in contract["forbidden_actions"]
    assert "no real order placement" in contract["forbidden_actions"]
    assert contract["single_input_handler"] == "handle_single_market_input"
    assert contract["batch_input_handler"] == "handle_batch_market_input"


def test_handle_single_market_input_returns_success_response():
    response = handle_single_market_input(
        raw=_sample_raw_market_data(),
        correlation_id="p3-d6-single-api",
    )

    assert response["ok"] is True
    assert response["api"] == API_NAME
    assert response["api_version"] == API_VERSION
    assert response["error"] is None
    assert response["data"]["status"] == "completed"
    assert response["data"]["pipeline"] == "market_input_pipeline"
    assert response["data"]["symbol"] == "BTCUSDT"
    assert response["data"]["market_type"] == "perpetual"
    assert response["data"]["event_count"] == 1
    assert response["data"]["replay"]["status"] == "completed"


def test_handle_single_market_input_can_persist(tmp_path):
    output_path = tmp_path / "local_api_single.jsonl"

    response = handle_single_market_input(
        raw=_sample_raw_market_data(),
        correlation_id="p3-d6-single-api-persist",
        output_path=str(output_path),
    )

    assert response["ok"] is True
    assert output_path.exists()
    assert response["data"]["persisted"] is True
    assert response["data"]["output_path"] == str(output_path)
    assert response["data"]["replay"]["event_count"] == 1


def test_handle_single_market_input_returns_error_response_for_bad_input():
    raw = _sample_raw_market_data()
    raw["last_price"] = "bad-number"

    response = handle_single_market_input(
        raw=raw,
        correlation_id="p3-d6-bad-single-api",
    )

    assert response["ok"] is False
    assert response["api"] == API_NAME
    assert response["data"] is None
    assert response["error"]["type"] == "ValueError"
    assert "last_price" in response["error"]["message"]


def test_handle_batch_market_input_returns_success_response(tmp_path):
    output_path = tmp_path / "local_api_batch.jsonl"

    response = handle_batch_market_input(
        rows=_fixture_rows(),
        correlation_id="p3-d6-batch-api",
        output_path=str(output_path),
    )

    assert response["ok"] is True
    assert output_path.exists()
    assert response["data"]["status"] == "completed"
    assert response["data"]["event_count"] == 2
    assert response["data"]["symbols"] == ["BTCUSDT", "ETHUSDT"]
    assert response["data"]["replay"]["status"] == "completed"
    assert response["data"]["replay"]["event_count"] == 2


def test_handle_batch_market_input_returns_error_response_for_bad_row():
    rows = _fixture_rows()
    rows[0]["market_type"] = "not-real"

    response = handle_batch_market_input(
        rows=rows,
        correlation_id="p3-d6-bad-batch-api",
    )

    assert response["ok"] is False
    assert response["data"] is None
    assert response["error"]["type"] == "ValueError"
    assert "market_type" in response["error"]["message"]
