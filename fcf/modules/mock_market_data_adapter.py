from typing import Any, Dict, List, Optional

from fcf.contracts.event import FCFEvent, create_event
from fcf.contracts.market_constants import (
    validate_asset_class,
    validate_market_type,
)


REQUIRED_FIELDS = [
    "asset_class",
    "symbol",
    "venue",
    "market_type",
    "timestamp",
    "timeframe",
    "last_price",
    "source",
]


NUMERIC_FIELDS = [
    "open",
    "high",
    "low",
    "close",
    "last_price",
    "volume",
    "quote_volume",
    "best_bid",
    "best_ask",
    "bid_depth",
    "ask_depth",
]


def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def missing_required_fields(raw: Dict[str, Any]) -> List[str]:
    missing = []

    for field_name in REQUIRED_FIELDS:
        value = raw.get(field_name)

        if value is None or value == "":
            missing.append(field_name)

    return missing


def validate_mock_market_data(raw: Dict[str, Any]) -> None:
    missing = missing_required_fields(raw)

    if missing:
        raise ValueError(f"missing required raw market fields: {missing}")

    validate_asset_class(raw.get("asset_class"))
    validate_market_type(raw.get("market_type"))

    if _to_float(raw.get("last_price")) is None:
        raise ValueError("missing or invalid required numeric field: last_price")

    for field_name in NUMERIC_FIELDS:
        if raw.get(field_name) is None:
            continue

        if _to_float(raw.get(field_name)) is None:
            raise ValueError(f"invalid numeric field: {field_name}")


def build_raw_market_payload(raw: Dict[str, Any]) -> Dict[str, Any]:
    validate_mock_market_data(raw)

    asset_class = validate_asset_class(raw.get("asset_class"))
    market_type = validate_market_type(raw.get("market_type"))

    timestamp = raw["timestamp"]

    return {
        "asset_class": asset_class,
        "symbol": raw["symbol"],
        "venue": raw["venue"],
        "market_type": market_type,
        "timestamp": timestamp,
        "timeframe": raw["timeframe"],
        "source": raw["source"],
        "source_type": raw.get("source_type", "mock"),
        "received_at": raw.get("received_at", timestamp),
        "prices": {
            "open": _to_float(raw.get("open")),
            "high": _to_float(raw.get("high")),
            "low": _to_float(raw.get("low")),
            "close": _to_float(raw.get("close")),
            "last_price": _to_float(raw.get("last_price")),
        },
        "liquidity": {
            "volume": _to_float(raw.get("volume")),
            "quote_volume": _to_float(raw.get("quote_volume")),
            "best_bid": _to_float(raw.get("best_bid")),
            "best_ask": _to_float(raw.get("best_ask")),
            "bid_depth": _to_float(raw.get("bid_depth")),
            "ask_depth": _to_float(raw.get("ask_depth")),
        },
        "raw": dict(raw),
        "metadata": raw.get("metadata", {}),
    }


def build_raw_market_event(
    raw: Dict[str, Any],
    correlation_id: str,
) -> FCFEvent:
    payload = build_raw_market_payload(raw)

    return create_event(
        event_name="fcf.market.raw_received",
        source_module="mock_market_data_adapter",
        correlation_id=correlation_id,
        payload=payload,
    )
