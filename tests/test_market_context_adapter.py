from fcf.contracts.event import create_event
from fcf.core.event_store import EventStore
from fcf.modules.market_context_adapter import (
    btc_market_context_to_base,
    btc_market_context_to_event_payload,
)
from fcf.modules.market_context_builder import build_btc_market_context
from fcf.replay.replay_engine import ReplayEngine


def _sample_btc_context():
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
        "mark_price": "60049",
        "index_price": "60048",
        "volume": "120.5",
        "quote_volume": "7230000",
        "best_bid": "60049.5",
        "best_ask": "60050.5",
        "bid_depth": "100",
        "ask_depth": "80",
        "realized_volatility": "0.012",
        "atr": "300",
        "price_change_1m": "0.001",
        "price_change_5m": "0.004",
        "price_change_15m": "0.008",
        "volatility_regime": "normal",
        "trend_direction": "up",
        "regime_label": "trend",
        "liquidity_level": "normal",
        "market_liquidity_risk": "low",
        "volatility_risk": "medium",
        "slippage_risk": "low",
        "metadata": {
            "source": "unit_test",
            "stage": "p2_d7",
        },
    }

    return build_btc_market_context(raw)


def test_btc_market_context_converts_to_base_market_context():
    btc_context = _sample_btc_context()

    base_context = btc_market_context_to_base(btc_context)

    assert base_context.asset_class == "crypto"
    assert base_context.symbol == "BTCUSDT"
    assert base_context.venue == "binance"
    assert base_context.market_type == "perpetual"
    assert base_context.currency == "BTC"
    assert base_context.quote_currency == "USDT"
    assert base_context.last_price == 60050.0
    assert base_context.reference_price == 60048.0
    assert base_context.settlement_price == 60049.0
    assert base_context.spread == 1.0
    assert round(base_context.to_dict()["spread"], 4) == 1.0
    assert base_context.regime_label == "trend"
    assert base_context.data_quality_level == "good"
    assert base_context.metadata["source_context_type"] == "BTCMarketContext"


def test_btc_market_context_event_payload_contains_base_and_source_context():
    btc_context = _sample_btc_context()

    payload = btc_market_context_to_event_payload(btc_context)

    assert payload["asset_class"] == "crypto"
    assert payload["context_type"] == "BaseMarketContext"
    assert payload["source_context_type"] == "BTCMarketContext"
    assert payload["base_market_context"]["asset_class"] == "crypto"
    assert payload["base_market_context"]["symbol"] == "BTCUSDT"
    assert payload["base_market_context"]["venue"] == "binance"
    assert payload["source_market_context"]["symbol"] == "BTCUSDT"
    assert payload["source_market_context"]["exchange"] == "binance"


def test_converted_market_context_can_be_recorded_and_replayed(tmp_path):
    btc_context = _sample_btc_context()
    payload = btc_market_context_to_event_payload(btc_context)

    event = create_event(
        event_name="fcf.market.context_adapted",
        source_module="market_context_adapter",
        correlation_id="p2-d7-market-context-adapter",
        payload=payload,
    )

    store = EventStore()
    store.record(event)

    file_path = tmp_path / "adapted_market_context_events.jsonl"
    store.save_jsonl(str(file_path))

    loaded_store = EventStore.load_jsonl(str(file_path))
    loaded_events = loaded_store.all_events()

    assert loaded_store.count() == 1
    assert loaded_events[0].event_name == "fcf.market.context_adapted"
    assert loaded_events[0].payload["asset_class"] == "crypto"
    assert loaded_events[0].payload["base_market_context"]["symbol"] == "BTCUSDT"
    assert loaded_events[0].payload["source_market_context"]["symbol"] == "BTCUSDT"

    replay_engine = ReplayEngine()
    result = replay_engine.replay(loaded_store.all_events())

    assert result["status"] == "completed"
    assert result["event_count"] == 1
    assert result["event_names"] == ["fcf.market.context_adapted"]
    assert result["is_sequence_ordered"] is True
    assert result["mismatch_count"] == 0
