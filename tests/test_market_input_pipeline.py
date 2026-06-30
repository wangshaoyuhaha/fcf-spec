import json
from pathlib import Path

import pytest

from fcf.pipelines.market_input_pipeline import (
    process_raw_market_batch,
    process_raw_market_input,
)


def _sample_raw_market_data():
    return {
        "asset_class": "crypto",
        "symbol": "BTCUSDT",
        "venue": "binance",
        "market_type": "perp",
        "timestamp": "2026-06-30T00:00:00Z",
        "timeframe": "1m",
        "source": "unit_test_pipeline",
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


def test_process_raw_market_input_returns_external_summary():
    result = process_raw_market_input(
        raw=_sample_raw_market_data(),
        correlation_id="p3-d4-single-input",
    )

    assert result["status"] == "completed"
    assert result["pipeline"] == "market_input_pipeline"
    assert result["correlation_id"] == "p3-d4-single-input"
    assert result["persisted"] is False
    assert result["event_count"] == 1
    assert result["event_name"] == "fcf.market.raw_received"
    assert result["asset_class"] == "crypto"
    assert result["symbol"] == "BTCUSDT"
    assert result["venue"] == "binance"
    assert result["market_type"] == "perpetual"
    assert result["timeframe"] == "1m"
    assert result["last_price"] == 60050.0
    assert result["source"] == "unit_test_pipeline"
    assert result["source_type"] == "mock"
    assert result["replay"]["status"] == "completed"
    assert result["replay"]["event_count"] == 1
    assert result["replay"]["event_names"] == ["fcf.market.raw_received"]


def test_process_raw_market_input_can_persist_and_replay(tmp_path):
    output_path = tmp_path / "single_market_input.jsonl"

    result = process_raw_market_input(
        raw=_sample_raw_market_data(),
        correlation_id="p3-d4-single-input-persisted",
        output_path=str(output_path),
    )

    assert result["persisted"] is True
    assert result["output_path"] == str(output_path)
    assert output_path.exists()
    assert result["replay"]["status"] == "completed"
    assert result["replay"]["event_count"] == 1
    assert result["replay"]["is_sequence_ordered"] is True
    assert result["replay"]["mismatch_count"] == 0


def test_process_raw_market_batch_uses_fixture_rows(tmp_path):
    output_path = tmp_path / "batch_market_input.jsonl"

    result = process_raw_market_batch(
        rows=_fixture_rows(),
        correlation_id="p3-d4-batch-input",
        output_path=str(output_path),
    )

    assert result["status"] == "completed"
    assert result["pipeline"] == "market_input_pipeline"
    assert result["persisted"] is True
    assert result["output_path"] == str(output_path)
    assert result["event_count"] == 2
    assert result["symbols"] == ["BTCUSDT", "ETHUSDT"]
    assert result["event_names"] == [
        "fcf.market.raw_received",
        "fcf.market.raw_received",
    ]
    assert result["replay"]["status"] == "completed"
    assert result["replay"]["event_count"] == 2
    assert result["replay"]["is_sequence_ordered"] is True
    assert result["replay"]["mismatch_count"] == 0


def test_process_raw_market_input_rejects_invalid_input():
    raw = _sample_raw_market_data()
    raw["last_price"] = "bad-number"

    with pytest.raises(ValueError):
        process_raw_market_input(
            raw=raw,
            correlation_id="p3-d4-invalid-input",
        )
