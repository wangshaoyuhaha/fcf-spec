from typing import Any, Dict, List, Optional

from fcf.core.event_store import EventStore
from fcf.modules.mock_market_data_adapter import build_raw_market_event
from fcf.replay.replay_engine import ReplayEngine


def process_raw_market_input(
    raw: Dict[str, Any],
    correlation_id: str,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    event = build_raw_market_event(
        raw=raw,
        correlation_id=correlation_id,
    )

    store = EventStore()
    store.record(event)

    persisted = False
    replay_source_events = store.all_events()

    if output_path is not None:
        store.save_jsonl(output_path)
        persisted = True
        loaded_store = EventStore.load_jsonl(output_path)
        replay_source_events = loaded_store.all_events()

    replay_engine = ReplayEngine()
    replay_result = replay_engine.replay(replay_source_events)

    return {
        "status": "completed",
        "pipeline": "market_input_pipeline",
        "correlation_id": correlation_id,
        "persisted": persisted,
        "output_path": output_path,
        "event_count": store.count(),
        "event_name": event.event_name,
        "event_id": event.event_id,
        "asset_class": event.payload["asset_class"],
        "symbol": event.payload["symbol"],
        "venue": event.payload["venue"],
        "market_type": event.payload["market_type"],
        "timeframe": event.payload["timeframe"],
        "last_price": event.payload["prices"]["last_price"],
        "source": event.payload["source"],
        "source_type": event.payload["source_type"],
        "replay": replay_result,
    }


def process_raw_market_batch(
    rows: List[Dict[str, Any]],
    correlation_id: str,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    store = EventStore()

    symbols = []
    event_ids = []

    for index, raw in enumerate(rows):
        event = build_raw_market_event(
            raw=raw,
            correlation_id=f"{correlation_id}-{index + 1}",
        )
        store.record(event)
        symbols.append(event.payload["symbol"])
        event_ids.append(event.event_id)

    persisted = False
    replay_source_events = store.all_events()

    if output_path is not None:
        store.save_jsonl(output_path)
        persisted = True
        loaded_store = EventStore.load_jsonl(output_path)
        replay_source_events = loaded_store.all_events()

    replay_engine = ReplayEngine()
    replay_result = replay_engine.replay(replay_source_events)

    return {
        "status": "completed",
        "pipeline": "market_input_pipeline",
        "correlation_id": correlation_id,
        "persisted": persisted,
        "output_path": output_path,
        "event_count": store.count(),
        "event_names": [event.event_name for event in replay_source_events],
        "event_ids": event_ids,
        "symbols": symbols,
        "replay": replay_result,
    }
