from fcf.contracts.event import create_event
from fcf.core.event_store import EventStore
from fcf.modules.market_context_builder import build_btc_market_context
from fcf.replay.replay_engine import ReplayEngine


def _sample_raw_market_data():
    return {
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
        "quote_volume": "7230000",
        "best_bid": "60049.5",
        "best_ask": "60050.5",
        "bid_depth": "100",
        "ask_depth": "80",
        "funding_rate": "0.0001",
        "regime_label": "trend",
        "liquidity_level": "normal",
        "market_liquidity_risk": "low",
        "volatility_risk": "medium",
        "slippage_risk": "low",
        "metadata": {
            "adapter": "crypto_first_sample",
            "purpose": "p2_d4_event_flow_test",
        },
    }


def test_market_context_can_be_embedded_in_fcf_event_payload():
    context = build_btc_market_context(_sample_raw_market_data())

    event = create_event(
        event_name="fcf.market.context_built",
        source_module="market_context_builder",
        correlation_id="p2-d4-market-context-event",
        payload={
            "asset_class": "crypto",
            "market_context": context.to_dict(),
        },
    )

    assert event.event_name == "fcf.market.context_built"
    assert event.source_module == "market_context_builder"
    assert event.payload["asset_class"] == "crypto"
    assert event.payload["market_context"]["symbol"] == "BTCUSDT"
    assert event.payload["market_context"]["spread"] == 1.0
    assert round(event.payload["market_context"]["orderbook_imbalance"], 4) == 0.1111
    assert event.payload["market_context"]["data_quality_level"] == "good"


def test_event_store_can_persist_market_context_event(tmp_path):
    context = build_btc_market_context(_sample_raw_market_data())

    event = create_event(
        event_name="fcf.market.context_built",
        source_module="market_context_builder",
        correlation_id="p2-d4-market-context-persistence",
        payload={
            "asset_class": "crypto",
            "market_context": context.to_dict(),
        },
    )

    store = EventStore()
    store.record(event)

    file_path = tmp_path / "market_context_events.jsonl"
    store.save_jsonl(str(file_path))

    loaded_store = EventStore.load_jsonl(str(file_path))
    loaded_events = loaded_store.all_events()

    assert loaded_store.count() == 1
    assert loaded_events[0].event_name == "fcf.market.context_built"
    assert loaded_events[0].payload["asset_class"] == "crypto"
    assert loaded_events[0].payload["market_context"]["symbol"] == "BTCUSDT"
    assert loaded_events[0].payload["market_context"]["last_price"] == 60050.0
    assert loaded_events[0].payload["market_context"]["data_quality_level"] == "good"


def test_replay_engine_can_replay_market_context_event(tmp_path):
    context = build_btc_market_context(_sample_raw_market_data())

    event = create_event(
        event_name="fcf.market.context_built",
        source_module="market_context_builder",
        correlation_id="p2-d4-market-context-replay",
        payload={
            "asset_class": "crypto",
            "market_context": context.to_dict(),
        },
    )

    store = EventStore()
    store.record(event)

    file_path = tmp_path / "market_context_replay.jsonl"
    store.save_jsonl(str(file_path))

    loaded_store = EventStore.load_jsonl(str(file_path))

    replay_engine = ReplayEngine()
    result = replay_engine.replay(loaded_store.all_events())

    assert result["status"] == "completed"
    assert result["event_count"] == 1
    assert result["event_names"] == ["fcf.market.context_built"]
    assert result["is_sequence_ordered"] is True
    assert result["mismatch_count"] == 0
