from typing import Any, Dict, List, Optional

from fcf.schemas.schema_error_catalog import (
    invalid_enum_message,
    invalid_non_negative_number_message,
    invalid_number_message,
    invalid_payload_type_message,
    invalid_positive_number_message,
    invalid_spread_message,
    missing_fields_message,
)

SCHEMA_NAME = "raw_market_input_schema"
SCHEMA_VERSION = "0.1.0"

REQUIRED_FIELDS = [
    "asset_class",
    "symbol",
    "venue",
    "market_type",
    "timestamp",
    "timeframe",
    "source",
    "source_type",
    "last_price",
]

OPTIONAL_NUMBER_FIELDS = [
    "open",
    "high",
    "low",
    "close",
    "volume",
    "quote_volume",
    "best_bid",
    "best_ask",
    "bid_depth",
    "ask_depth",
]

SUPPORTED_ASSET_CLASSES = {
    "crypto",
    "equities",
    "fx",
    "commodities",
    "rates",
    "index",
    "futures",
    "options",
}

MARKET_TYPE_ALIASES = {
    "spot": "spot",
    "perp": "perpetual",
    "perpetual": "perpetual",
    "future": "futures",
    "futures": "futures",
    "option": "option",
    "options": "option",
}


def describe_schema() -> Dict[str, Any]:
    return {
        "schema": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "required_fields": list(REQUIRED_FIELDS),
        "optional_number_fields": list(OPTIONAL_NUMBER_FIELDS),
        "supported_asset_classes": sorted(SUPPORTED_ASSET_CLASSES),
        "supported_market_types": sorted(set(MARKET_TYPE_ALIASES.values())),
        "safe_boundary": {
            "no_real_exchange_api": True,
            "no_real_order_placement": True,
            "no_secret_storage": True,
        },
    }


def _require_mapping(raw: Dict[str, Any]) -> None:
    if not isinstance(raw, dict):
        raise ValueError(invalid_payload_type_message())


def _require_non_empty_string(raw: Dict[str, Any], field: str) -> str:
    value = raw.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be provided as non-empty string")
    return value.strip()


def check_required_fields(raw: Dict[str, Any]) -> None:
    _require_mapping(raw)

    missing: List[str] = []
    for field in REQUIRED_FIELDS:
        if field not in raw:
            missing.append(field)
        elif raw[field] is None:
            missing.append(field)
        elif isinstance(raw[field], str) and not raw[field].strip():
            missing.append(field)

    if missing:
        raise ValueError(missing_fields_message(missing))


def normalize_asset_class(asset_class: str) -> str:
    normalized = asset_class.strip().lower()
    if normalized not in SUPPORTED_ASSET_CLASSES:
        raise ValueError(invalid_enum_message("asset_class", asset_class))
    return normalized


def normalize_market_type(market_type: str) -> str:
    key = market_type.strip().lower()
    if key not in MARKET_TYPE_ALIASES:
        raise ValueError(invalid_enum_message("market_type", market_type))
    return MARKET_TYPE_ALIASES[key]


def to_float_field(raw: Dict[str, Any], field: str) -> Optional[float]:
    if field not in raw or raw[field] is None:
        return None

    value = raw[field]

    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None

    try:
        converted = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(invalid_number_message(field)) from error

    return converted


def _require_positive_number(value: Optional[float], field: str) -> float:
    if value is None:
        raise ValueError(invalid_number_message(field))
    if value <= 0:
        raise ValueError(invalid_positive_number_message(field))
    return value


def _require_non_negative_number(value: Optional[float], field: str) -> Optional[float]:
    if value is None:
        return None
    if value < 0:
        raise ValueError(invalid_non_negative_number_message(field))
    return value


def normalize_raw_market_input(raw: Dict[str, Any]) -> Dict[str, Any]:
    check_required_fields(raw)

    normalized: Dict[str, Any] = dict(raw)

    normalized["asset_class"] = normalize_asset_class(
        _require_non_empty_string(raw, "asset_class")
    )
    normalized["symbol"] = _require_non_empty_string(raw, "symbol").upper()
    normalized["venue"] = _require_non_empty_string(raw, "venue").lower()
    normalized["market_type"] = normalize_market_type(
        _require_non_empty_string(raw, "market_type")
    )
    normalized["timestamp"] = _require_non_empty_string(raw, "timestamp")
    normalized["timeframe"] = _require_non_empty_string(raw, "timeframe")
    normalized["source"] = _require_non_empty_string(raw, "source")
    normalized["source_type"] = _require_non_empty_string(raw, "source_type")

    last_price = to_float_field(raw, "last_price")
    normalized["last_price"] = _require_positive_number(last_price, "last_price")

    for field in OPTIONAL_NUMBER_FIELDS:
        value = to_float_field(raw, field)
        if value is not None:
            normalized[field] = value

    for field in ["volume", "quote_volume", "bid_depth", "ask_depth"]:
        if field in normalized:
            normalized[field] = _require_non_negative_number(normalized[field], field)

    best_bid = normalized.get("best_bid")
    best_ask = normalized.get("best_ask")
    if best_bid is not None and best_ask is not None and best_bid > best_ask:
        raise ValueError(invalid_spread_message())

    return normalized


def validate_raw_market_input(raw: Dict[str, Any]) -> Dict[str, Any]:
    normalized = normalize_raw_market_input(raw)
    return {
        "ok": True,
        "schema": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "error": None,
        "data": normalized,
    }
