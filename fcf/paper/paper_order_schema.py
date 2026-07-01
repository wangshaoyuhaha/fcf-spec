from typing import Any, Dict, Iterable, List, Optional

from fcf.schemas.raw_market_input_schema import (
    normalize_asset_class,
    normalize_market_type,
)

SCHEMA_NAME = "paper_order_schema"
SCHEMA_VERSION = "0.1.0"

REQUIRED_FIELDS = [
    "asset_class",
    "symbol",
    "venue",
    "market_type",
    "side",
    "order_type",
    "quantity",
    "source",
    "correlation_id",
]

SIDE_ALIASES = {
    "buy": "buy",
    "long": "buy",
    "sell": "sell",
    "short": "sell",
}

ORDER_TYPE_ALIASES = {
    "market": "market",
    "limit": "limit",
    "stop": "stop",
    "stop_limit": "stop_limit",
    "stop-limit": "stop_limit",
}

TIME_IN_FORCE_ALIASES = {
    "gtc": "GTC",
    "ioc": "IOC",
    "fok": "FOK",
    "day": "DAY",
}

DEFAULT_TIME_IN_FORCE = "GTC"


def describe_paper_order_schema() -> Dict[str, Any]:
    return {
        "schema": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "required_fields": list(REQUIRED_FIELDS),
        "optional_fields": [
            "price",
            "time_in_force",
            "metadata",
        ],
        "supported_sides": sorted(set(SIDE_ALIASES.values())),
        "supported_order_types": sorted(set(ORDER_TYPE_ALIASES.values())),
        "supported_time_in_force": sorted(set(TIME_IN_FORCE_ALIASES.values())),
        "forced_safety_fields": {
            "execution_mode": "paper",
            "real_order": False,
            "real_exchange_api": False,
            "real_money_impact": False,
        },
        "safe_boundary": {
            "no_real_exchange_api": True,
            "no_real_order_placement": True,
            "no_secret_storage": True,
        },
    }


def _require_mapping(raw: Dict[str, Any]) -> None:
    if not isinstance(raw, dict):
        raise ValueError("paper order must be a dict")


def _missing_fields_message(fields: Iterable[str]) -> str:
    return "missing required fields: " + ", ".join([str(field) for field in fields])


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
        raise ValueError(_missing_fields_message(missing))


def _require_non_empty_string(raw: Dict[str, Any], field: str) -> str:
    value = raw.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be provided as non-empty string")
    return value.strip()


def normalize_side(side: str) -> str:
    key = side.strip().lower()
    if key not in SIDE_ALIASES:
        raise ValueError(f"side is not supported: {side}")
    return SIDE_ALIASES[key]


def normalize_order_type(order_type: str) -> str:
    key = order_type.strip().lower()
    if key not in ORDER_TYPE_ALIASES:
        raise ValueError(f"order_type is not supported: {order_type}")
    return ORDER_TYPE_ALIASES[key]


def normalize_time_in_force(time_in_force: Optional[str]) -> str:
    if time_in_force is None:
        return DEFAULT_TIME_IN_FORCE

    if not isinstance(time_in_force, str) or not time_in_force.strip():
        return DEFAULT_TIME_IN_FORCE

    key = time_in_force.strip().lower()
    if key not in TIME_IN_FORCE_ALIASES:
        raise ValueError(f"time_in_force is not supported: {time_in_force}")

    return TIME_IN_FORCE_ALIASES[key]


def to_float_field(raw: Dict[str, Any], field: str) -> Optional[float]:
    if field not in raw or raw[field] is None:
        return None

    value = raw[field]

    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None

    try:
        return float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field} must be a valid number") from error


def _require_positive_number(value: Optional[float], field: str) -> float:
    if value is None:
        raise ValueError(f"{field} must be a valid number")
    if value <= 0:
        raise ValueError(f"{field} must be greater than 0")
    return value


def _optional_positive_number(value: Optional[float], field: str) -> Optional[float]:
    if value is None:
        return None
    if value <= 0:
        raise ValueError(f"{field} must be greater than 0")
    return value


def normalize_paper_order(raw: Dict[str, Any]) -> Dict[str, Any]:
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
    normalized["side"] = normalize_side(_require_non_empty_string(raw, "side"))
    normalized["order_type"] = normalize_order_type(
        _require_non_empty_string(raw, "order_type")
    )
    normalized["quantity"] = _require_positive_number(
        to_float_field(raw, "quantity"),
        "quantity",
    )

    price = _optional_positive_number(to_float_field(raw, "price"), "price")
    if price is not None:
        normalized["price"] = price
    elif "price" in normalized:
        del normalized["price"]

    normalized["time_in_force"] = normalize_time_in_force(raw.get("time_in_force"))
    normalized["source"] = _require_non_empty_string(raw, "source")
    normalized["correlation_id"] = _require_non_empty_string(raw, "correlation_id")

    metadata = raw.get("metadata", {})
    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a dict")
    normalized["metadata"] = metadata

    normalized["execution_mode"] = "paper"
    normalized["real_order"] = False
    normalized["real_exchange_api"] = False
    normalized["real_money_impact"] = False

    return normalized


def validate_paper_order(raw: Dict[str, Any]) -> Dict[str, Any]:
    normalized = normalize_paper_order(raw)

    return {
        "ok": True,
        "schema": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "error": None,
        "data": normalized,
    }
