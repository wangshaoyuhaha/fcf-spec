import pytest

from fcf.modules.market_context_builder import build_btc_market_context


def test_build_btc_market_context_calculates_spread_and_imbalance():
    raw = {
        "symbol": "BTCUSDT",
        "exchange": "binance",
        "market_type": "perpetual",
        "timestamp": "2026-06-30T00:00:00Z",
        "timeframe": "1m",
        "open": "60000",
        "high": "60100",
        "low": "59900",
        "close": "60050",
        "last_price": "60050",
        "volume": "120.5",
        "best_bid": "60049.5",
        "best_ask": "60050.5",
        "bid_depth": "100",
        "ask_depth": "80",
        "funding_rate": "0.0001",
        "regime_label": "trend",
    }

    context = build_btc_market_context(raw)

    assert context.symbol == "BTCUSDT"
    assert context.exchange == "binance"
    assert context.market_type == "perpetual"
    assert context.last_price == 60050.0
    assert context.volume == 120.5
    assert context.best_bid == 60049.5
    assert context.best_ask == 60050.5
    assert context.spread == 1.0
    assert round(context.orderbook_imbalance, 4) == 0.1111
    assert context.funding_rate == 0.0001
    assert context.regime_label == "trend"
    assert context.data_quality_level == "good"


def test_build_btc_market_context_keeps_existing_spread_and_imbalance():
    raw = {
        "symbol": "BTCUSDT",
        "exchange": "binance",
        "market_type": "spot",
        "timestamp": "2026-06-30T00:01:00Z",
        "timeframe": "5m",
        "open": 60000,
        "high": 60200,
        "low": 59800,
        "close": 60100,
        "last_price": 60100,
        "volume": 200,
        "best_bid": 60099,
        "best_ask": 60101,
        "spread": 2.0,
        "bid_depth": 50,
        "ask_depth": 50,
        "orderbook_imbalance": 0.25,
    }

    context = build_btc_market_context(raw)

    assert context.spread == 2.0
    assert context.orderbook_imbalance == 0.25
    assert context.data_quality_level == "good"


def test_build_btc_market_context_marks_partial_quality_without_orderbook():
    raw = {
        "symbol": "BTCUSDT",
        "exchange": "binance",
        "market_type": "perpetual",
        "timestamp": "2026-06-30T00:02:00Z",
        "timeframe": "15m",
        "open": 60000,
        "high": 60300,
        "low": 59900,
        "close": 60200,
        "last_price": 60200,
        "volume": 100,
    }

    context = build_btc_market_context(raw)

    assert context.spread is None
    assert context.orderbook_imbalance is None
    assert context.data_quality_level == "partial"


def test_build_btc_market_context_rejects_invalid_required_number():
    raw = {
        "symbol": "BTCUSDT",
        "exchange": "binance",
        "market_type": "perpetual",
        "timestamp": "2026-06-30T00:03:00Z",
        "timeframe": "1h",
        "open": "bad-number",
        "high": 60300,
        "low": 59900,
        "close": 60200,
        "last_price": 60200,
    }

    with pytest.raises(ValueError):
        build_btc_market_context(raw)
