from fcf.contracts.base_market_context import (
    BaseMarketContext,
    base_market_context_from_dict,
    normalize_asset_class,
)


def test_normalize_asset_class_accepts_supported_values():
    assert normalize_asset_class("crypto") == "crypto"
    assert normalize_asset_class("FX") == "fx"
    assert normalize_asset_class("Equity") == "equity"
    assert normalize_asset_class("futures") == "futures"
    assert normalize_asset_class("commodity") == "commodity"
    assert normalize_asset_class("rates") == "rates"
    assert normalize_asset_class("bond") == "bond"
    assert normalize_asset_class("index") == "index"


def test_normalize_asset_class_falls_back_to_unknown():
    assert normalize_asset_class(None) == "unknown"
    assert normalize_asset_class("") == "unknown"
    assert normalize_asset_class("unsupported-asset") == "unknown"


def test_base_market_context_to_dict_for_crypto():
    context = BaseMarketContext(
        asset_class="crypto",
        symbol="BTCUSDT",
        venue="binance",
        market_type="perpetual",
        timestamp="2026-06-30T00:00:00Z",
        timeframe="1m",
        currency="BTC",
        quote_currency="USDT",
        open=60000.0,
        high=60100.0,
        low=59900.0,
        close=60050.0,
        last_price=60050.0,
        best_bid=60049.5,
        best_ask=60050.5,
        spread=1.0,
        liquidity_level="normal",
        realized_volatility=0.012,
        regime_label="trend",
        data_quality_level="good",
        metadata={"source": "unit_test"},
    )

    data = context.to_dict()

    assert data["asset_class"] == "crypto"
    assert data["symbol"] == "BTCUSDT"
    assert data["venue"] == "binance"
    assert data["market_type"] == "perpetual"
    assert data["last_price"] == 60050.0
    assert data["spread"] == 1.0
    assert data["regime_label"] == "trend"
    assert data["data_quality_level"] == "good"
    assert data["metadata"]["source"] == "unit_test"


def test_base_market_context_to_dict_for_equity():
    context = BaseMarketContext(
        asset_class="equity",
        symbol="AAPL",
        venue="nasdaq",
        market_type="cash",
        timestamp="2026-06-30T14:30:00Z",
        timeframe="1m",
        currency="USD",
        open=200.0,
        high=201.0,
        low=199.5,
        close=200.5,
        last_price=200.5,
        volume=1000000.0,
        liquidity_level="high",
        data_quality_level="good",
    )

    data = context.to_dict()

    assert data["asset_class"] == "equity"
    assert data["symbol"] == "AAPL"
    assert data["venue"] == "nasdaq"
    assert data["market_type"] == "cash"
    assert data["currency"] == "USD"
    assert data["volume"] == 1000000.0
    assert data["liquidity_level"] == "high"


def test_base_market_context_from_dict_round_trip():
    original = BaseMarketContext(
        asset_class="futures",
        symbol="ES",
        venue="cme",
        market_type="future",
        timestamp="2026-06-30T14:31:00Z",
        timeframe="5m",
        currency="USD",
        open=5500.0,
        high=5510.0,
        low=5490.0,
        close=5505.0,
        last_price=5505.0,
        settlement_price=5504.5,
        volume=50000.0,
        best_bid=5504.75,
        best_ask=5505.25,
        spread=0.5,
        liquidity_level="high",
        realized_volatility=0.008,
        volatility_regime="normal",
        trend_direction="up",
        regime_label="trend",
        data_quality_level="good",
        market_liquidity_risk="low",
        volatility_risk="low",
        metadata={"contract": "front_month"},
    )

    loaded = base_market_context_from_dict(original.to_dict())

    assert loaded == original
    assert loaded.metadata["contract"] == "front_month"


def test_base_market_context_defaults_are_safe():
    context = BaseMarketContext(
        asset_class="unknown",
        symbol="UNKNOWN",
        venue="unknown",
        market_type="unknown",
        timestamp="2026-06-30T00:00:00Z",
        timeframe="1m",
    )

    assert context.normalized_asset_class() == "unknown"
    assert context.liquidity_level == "unknown"
    assert context.volatility_regime == "unknown"
    assert context.regime_label == "unknown"
    assert context.data_quality_level == "unknown"
    assert context.abnormal_move_detected is False
    assert context.metadata == {}
