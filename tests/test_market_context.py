from fcf.contracts.market_context import BTCMarketContext, market_context_from_dict


def test_btc_market_context_to_dict():
    context = BTCMarketContext(
        symbol="BTCUSDT",
        exchange="binance",
        market_type="perpetual",
        timestamp="2026-06-30T00:00:00Z",
        timeframe="1m",
        open=60000.0,
        high=60100.0,
        low=59900.0,
        close=60050.0,
        last_price=60050.0,
        volume=120.5,
        quote_volume=7230000.0,
        best_bid=60049.5,
        best_ask=60050.5,
        spread=1.0,
        funding_rate=0.0001,
        realized_volatility=0.012,
        regime_label="trend",
        liquidity_level="normal",
        data_quality_level="good",
    )

    data = context.to_dict()

    assert data["symbol"] == "BTCUSDT"
    assert data["exchange"] == "binance"
    assert data["market_type"] == "perpetual"
    assert data["timeframe"] == "1m"
    assert data["last_price"] == 60050.0
    assert data["spread"] == 1.0
    assert data["funding_rate"] == 0.0001
    assert data["regime_label"] == "trend"
    assert data["data_quality_level"] == "good"


def test_market_context_from_dict_round_trip():
    original = BTCMarketContext(
        symbol="BTCUSDT",
        exchange="binance",
        market_type="perpetual",
        timestamp="2026-06-30T00:01:00Z",
        timeframe="5m",
        open=60000.0,
        high=60200.0,
        low=59800.0,
        close=60100.0,
        last_price=60100.0,
        mark_price=60098.0,
        index_price=60095.0,
        volume=250.0,
        quote_volume=15025000.0,
        best_bid=60099.5,
        best_ask=60100.5,
        spread=1.0,
        bid_depth=100.0,
        ask_depth=90.0,
        orderbook_imbalance=0.0526,
        funding_rate=0.0002,
        open_interest=120000.0,
        realized_volatility=0.018,
        atr=320.0,
        volatility_regime="high",
        trend_direction="up",
        regime_label="breakout",
        liquidity_level="normal",
        abnormal_move_detected=False,
        data_quality_level="good",
        market_liquidity_risk="low",
        volatility_risk="medium",
        slippage_risk="low",
        metadata={"source": "unit_test"},
    )

    loaded = market_context_from_dict(original.to_dict())

    assert loaded == original
    assert loaded.metadata["source"] == "unit_test"


def test_market_context_defaults():
    context = BTCMarketContext(
        symbol="BTCUSDT",
        exchange="binance",
        market_type="spot",
        timestamp="2026-06-30T00:02:00Z",
        timeframe="15m",
        open=60000.0,
        high=60300.0,
        low=59900.0,
        close=60200.0,
        last_price=60200.0,
    )

    assert context.volume == 0.0
    assert context.regime_label == "unknown"
    assert context.data_quality_level == "unknown"
    assert context.abnormal_move_detected is False
    assert context.metadata == {}
