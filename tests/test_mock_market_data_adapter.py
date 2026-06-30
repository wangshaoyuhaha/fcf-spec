import pytest

from fcf.core.event_store import EventStore
from fcf.modules.mock_market_data_adapter import (
    build_raw_market_event,
    build_raw_market_payload,
    missing_required_fields,
    validate_mock_market_data,
)
from fcf.replay.replay_engine import ReplayEngine


def _sample_raw_crypto_market_data():
    return {
        "asset_class": "crypto",
        "symbol": "BTCUSDT",
        "venue": "binance",
        "market_type": "perp",
        "timestamp": "2026-06-30T00:00:00Z",
        "timeframe": "1m",
        "source": "unit_test_mock",
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
        "metadata": {
            "stage": "p3_d2",
            "purpose": "mock_market_data_adapter_test",
        },
    }


def test_missing_required_fields_detects_missing_values():
    raw = {
        "asset_class": "crypto",
        "symbol": "BTCUSDT",
    }

    missing = missing_required_fields(raw)

    assert "venue" in missing
    assert "market_type" in missing
    assert "timestamp" in missing
    assert "timeframe" in missing
    assert "last_price" in missing
    assert "source" in missing


def test_validate_mock_market_data_accepts_valid_raw_dict():
    raw = _sample_raw_crypto_market_data()

    validate_mock_market_data(raw)


def test_validate_mock_market_data_rejects_bad_asset_class():
    raw = _sample_raw_crypto_market_data()
    raw["asset_class"] = "not-real"

    with pytest.raises(ValueError):
        validate_mock_market_data(raw)


def test_validate_mock_market_data_rejects_bad_market_type():
    raw = _sample_raw_crypto_market_data()
    raw["market_type"] = "not-real"

    with pytest.raises(ValueError):
        validate_mock_market_data(raw)


def test_validate_mock_market_data_rejects_bad_numeric_field():
    raw = _sample_raw_crypto_market_data()
    raw["last_price"] = "bad-number"

    with pytest.raises(ValueError):
        validate_mock_market_data(raw)


def test_build_raw_market_payload_normalizes_and_groups_fields():
    raw = _sample_raw_crypto_market_data()

    payload = build_raw_market_payload(raw)

    assert payload["asset_class"] == "crypto"
    assert payload["symbol"] == "BTCUSDT"
    assert payload["venue"] == "binance"
    assert payload["market_type"] == "perpetual"
    assert payload["source"] == "unit_test_mock"
    assert payload["source_type"] == "mock"
    assert payload["received_at"] == "2026-06-30T00:00:00Z"
    assert payload["prices"]["last_price"] == 60050.0
    assert payload["liquidity"]["volume"] == 120.5
    assert payload["liquidity"]["best_bid"] == 60049.5
    assert payload["liquidity"]["best_ask"] == 60050.5
    assert payload["metadata"]["stage"] == "p3_d2"
    assert payload["raw"]["symbol"] == "BTCUSDT"


def test_build_raw_market_event_creates_fcf_event():
    raw = _sample_raw_crypto_market_data()

    event = build_raw_market_event(
        raw=raw,
        correlation_id="p3-d2-raw-market-event",
    )

    assert event.event_name == "fcf.market.raw_received"
    assert event.source_module == "mock_market_data_adapter"
    assert event.correlation_id == "p3-d2-raw-market-event"
    assert event.payload["asset_class"] == "crypto"
    assert event.payload["market_type"] == "perpetual"
    assert event.payload["prices"]["last_price"] == 60050.0


def test_raw_market_event_can_be_persisted_and_replayed(tmp_path):
    raw = _sample_raw_crypto_market_data()

    event = build_raw_market_event(
        raw=raw,
        correlation_id="p3-d2-raw-market-replay",
    )

    store = EventStore()
    store.record(event)

    file_path = tmp_path / "raw_market_events.jsonl"
    store.save_jsonl(str(file_path))

    loaded_store = EventStore.load_jsonl(str(file_path))
    loaded_events = loaded_store.all_events()

    assert loaded_store.count() == 1
    assert loaded_events[0].event_name == "fcf.market.raw_received"
    assert loaded_events[0].payload["symbol"] == "BTCUSDT"
    assert loaded_events[0].payload["market_type"] == "perpetual"

    replay_engine = ReplayEngine()
    result = replay_engine.replay(loaded_events)

    assert result["status"] == "completed"
    assert result["event_count"] == 1
    assert result["event_names"] == ["fcf.market.raw_received"]
    assert result["is_sequence_ordered"] is True
    assert result["mismatch_count"] == 0
