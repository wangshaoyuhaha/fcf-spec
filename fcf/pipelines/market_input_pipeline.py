from typing import Any, Dict, List, Optional

from fcf.contracts.event import create_event
from fcf.core.event_store import EventStore
from fcf.replay.replay_engine import ReplayEngine
from fcf.schemas.raw_market_input_schema import (
    SCHEMA_NAME,
    SCHEMA_VERSION,
    normalize_raw_market_input,
)

PIPELINE_NAME = "market_input_pipeline"
RAW_MARKET_EVENT_NAME = "fcf.market.raw_received"


def _build_raw_market_event(
    normalized_raw: Dict[str, Any],
    correlation_id: str,
) -> Any:
    return create_event(
        event_name=RAW_MARKET_EVENT_NAME,
        source_module=PIPELINE_NAME,
        correlation_id=correlation_id,
        payload={
            "raw_market_input": normalized_raw,
        },
        metadata={
            "schema": SCHEMA_NAME,
            "schema_version": SCHEMA_VERSION,
        },
    )


def _persist_if_needed(store: EventStore, output_path: Optional[str]) -> bool:
    if output_path:
        store.save_jsonl(output_path)
        return True
    return False


def _replay_store(store: EventStore) -> Dict[str, Any]:
    replay_engine = ReplayEngine()
    return replay_engine.replay(store.all_events())


def process_raw_market_input(
    raw: Dict[str, Any],
    correlation_id: str,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    normalized_raw = normalize_raw_market_input(raw)

    store = EventStore()
    event = _build_raw_market_event(
        normalized_raw=normalized_raw,
        correlation_id=correlation_id,
    )
    store.record(event)

    persisted = _persist_if_needed(store, output_path)
    replay_result = _replay_store(store)

    return {
        "status": "completed",
        "pipeline": PIPELINE_NAME,
        "correlation_id": correlation_id,
        "schema": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "event_count": store.count(),
        "event_name": RAW_MARKET_EVENT_NAME,
        "event_names": replay_result.get("event_names", [RAW_MARKET_EVENT_NAME]),
        "asset_class": normalized_raw["asset_class"],
        "symbol": normalized_raw["symbol"],
        "venue": normalized_raw["venue"],
        "market_type": normalized_raw["market_type"],
        "timeframe": normalized_raw["timeframe"],
        "timestamp": normalized_raw["timestamp"],
        "source": normalized_raw["source"],
        "source_type": normalized_raw["source_type"],
        "last_price": normalized_raw["last_price"],
        "persisted": persisted,
        "output_path": output_path,
        "replay": replay_result,
    }


def process_raw_market_batch(
    rows: List[Dict[str, Any]],
    correlation_id: str,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    if not isinstance(rows, list):
        raise ValueError("rows must be provided as list")

    store = EventStore()
    normalized_rows: List[Dict[str, Any]] = []

    for row in rows:
        normalized_raw = normalize_raw_market_input(row)
        normalized_rows.append(normalized_raw)

        event = _build_raw_market_event(
            normalized_raw=normalized_raw,
            correlation_id=correlation_id,
        )
        store.record(event)

    persisted = _persist_if_needed(store, output_path)
    replay_result = _replay_store(store)

    return {
        "status": "completed",
        "pipeline": PIPELINE_NAME,
        "correlation_id": correlation_id,
        "schema": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "event_count": store.count(),
        "event_names": replay_result.get(
            "event_names",
            [RAW_MARKET_EVENT_NAME for _ in normalized_rows],
        ),
        "symbols": [row["symbol"] for row in normalized_rows],
        "asset_classes": [row["asset_class"] for row in normalized_rows],
        "market_types": [row["market_type"] for row in normalized_rows],
        "timeframes": [row["timeframe"] for row in normalized_rows],
        "persisted": persisted,
        "output_path": output_path,
        "replay": replay_result,
    }
