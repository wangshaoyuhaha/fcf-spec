import json
from pathlib import Path

from fcf.core.event_store import EventStore
from fcf.modules.mock_market_data_adapter import build_raw_market_event
from fcf.replay.replay_engine import ReplayEngine


FIXTURE_PATH = Path("fixtures/raw_market_data_crypto.json")


def load_fixture_rows():
    with FIXTURE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_crypto_raw_market_fixture_exists_and_loads():
    rows = load_fixture_rows()

    assert len(rows) == 2
    assert rows[0]["symbol"] == "BTCUSDT"
    assert rows[1]["symbol"] == "ETHUSDT"
    assert rows[0]["source_type"] == "fixture"


def test_crypto_raw_market_fixture_builds_raw_market_events():
    rows = load_fixture_rows()

    events = [
        build_raw_market_event(
            raw=row,
            correlation_id=f"p3-d3-fixture-{index + 1}",
        )
        for index, row in enumerate(rows)
    ]

    assert len(events) == 2
    assert events[0].event_name == "fcf.market.raw_received"
    assert events[1].event_name == "fcf.market.raw_received"
    assert events[0].payload["symbol"] == "BTCUSDT"
    assert events[1].payload["symbol"] == "ETHUSDT"
    assert events[0].payload["market_type"] == "perpetual"
    assert events[1].payload["market_type"] == "spot"


def test_crypto_raw_market_fixture_can_be_persisted_and_replayed(tmp_path):
    rows = load_fixture_rows()

    store = EventStore()

    for index, row in enumerate(rows):
        event = build_raw_market_event(
            raw=row,
            correlation_id=f"p3-d3-fixture-replay-{index + 1}",
        )
        store.record(event)

    file_path = tmp_path / "fixture_raw_market_events.jsonl"
    store.save_jsonl(str(file_path))

    loaded_store = EventStore.load_jsonl(str(file_path))
    loaded_events = loaded_store.all_events()

    assert loaded_store.count() == 2
    assert loaded_events[0].payload["symbol"] == "BTCUSDT"
    assert loaded_events[1].payload["symbol"] == "ETHUSDT"

    replay_engine = ReplayEngine()
    result = replay_engine.replay(loaded_events)

    assert result["status"] == "completed"
    assert result["event_count"] == 2
    assert result["event_names"] == [
        "fcf.market.raw_received",
        "fcf.market.raw_received",
    ]
    assert result["is_sequence_ordered"] is True
    assert result["mismatch_count"] == 0
