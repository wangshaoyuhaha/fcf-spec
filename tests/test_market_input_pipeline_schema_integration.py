import pytest

from fcf.pipelines.market_input_pipeline import (
    process_raw_market_batch,
    process_raw_market_input,
)


def _sample_raw_market_data():
    return {
        "asset_class": "Crypto",
        "symbol": "btcusdt",
        "venue": "BINANCE",
        "market_type": "PERP",
        "timestamp": "2026-06-30T00:00:00Z",
        "timeframe": "1m",
        "source": "unit_test_pipeline_schema",
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


def test_process_raw_market_input_uses_schema_normalization():
    result = process_raw_market_input(
        raw=_sample_raw_market_data(),
        correlation_id="p4-d3-single-schema",
    )

    assert result["status"] == "completed"
    assert result["pipeline"] == "market_input_pipeline"
    assert result["schema"] == "raw_market_input_schema"
    assert result["schema_version"] == "0.1.0"
    assert result["asset_class"] == "crypto"
    assert result["symbol"] == "BTCUSDT"
    assert result["venue"] == "binance"
    assert result["market_type"] == "perpetual"
    assert result["event_count"] == 1
    assert result["replay"]["status"] == "completed"
    assert result["replay"]["event_count"] == 1


def test_process_raw_market_batch_uses_schema_normalization():
    btc = _sample_raw_market_data()
    eth = _sample_raw_market_data()
    eth["symbol"] = "ethusdt"
    eth["market_type"] = "spot"
    eth["last_price"] = "3305"
    eth["best_bid"] = "3304.9"
    eth["best_ask"] = "3305.1"

    result = process_raw_market_batch(
        rows=[btc, eth],
        correlation_id="p4-d3-batch-schema",
    )

    assert result["status"] == "completed"
    assert result["schema"] == "raw_market_input_schema"
    assert result["event_count"] == 2
    assert result["symbols"] == ["BTCUSDT", "ETHUSDT"]
    assert result["asset_classes"] == ["crypto", "crypto"]
    assert result["market_types"] == ["perpetual", "spot"]
    assert result["replay"]["event_count"] == 2


def test_process_raw_market_input_rejects_schema_error():
    raw = _sample_raw_market_data()
    raw["best_bid"] = "60060"
    raw["best_ask"] = "60050"

    with pytest.raises(ValueError, match="best_bid"):
        process_raw_market_input(
            raw=raw,
            correlation_id="p4-d3-bad-spread",
        )
