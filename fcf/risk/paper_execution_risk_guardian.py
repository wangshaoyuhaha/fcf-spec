from typing import Any, Dict, List, Optional

GUARDIAN_NAME = "paper_execution_risk_guardian"
GUARDIAN_VERSION = "0.1.0"

DECISION_ALLOWED = "allowed"
DECISION_DENIED = "denied"

ERROR_TYPE_RISK_DENY = "RiskDeny"

SAFE_BOUNDARY = {
    "execution_mode": "paper",
    "real_order": False,
    "real_execution": False,
    "real_exchange_api": False,
    "real_money_impact": False,
    "no_real_exchange_api": True,
    "no_real_order_placement": True,
    "no_secret_storage": True,
    "risk_guardian_required": True,
}

RISK_RULES = [
    "request_must_be_dict",
    "raw_order_must_be_dict",
    "missing_risk_context",
    "max_quantity",
    "max_notional",
    "duplicate_order_key",
    "blocked_symbol",
    "blocked_asset_class",
    "leverage_requested",
    "margin_requested",
    "high_risk_flags",
]

LEVERAGE_FIELDS = {
    "leverage",
    "leverage_requested",
}

MARGIN_FIELDS = {
    "margin",
    "margin_mode",
    "margin_requested",
}


def describe_paper_execution_risk_guardian() -> Dict[str, Any]:
    return {
        "guardian": GUARDIAN_NAME,
        "guardian_version": GUARDIAN_VERSION,
        "risk_rules": list(RISK_RULES),
        "decision_values": [
            DECISION_ALLOWED,
            DECISION_DENIED,
        ],
        "stable_response_fields": [
            "ok",
            "guardian",
            "guardian_version",
            "decision",
            "error",
            "data",
        ],
        "safe_boundary": dict(SAFE_BOUNDARY),
    }


def _truthy(value: Any) -> bool:
    if value is True:
        return True

    if isinstance(value, str):
        return value.strip().lower() in {
            "true",
            "yes",
            "y",
            "1",
            "on",
        }

    if isinstance(value, (int, float)):
        return value == 1

    return False


def _requested(value: Any) -> bool:
    if value is None:
        return False

    if value is False:
        return False

    if isinstance(value, str):
        return value.strip() != "" and value.strip().lower() not in {
            "false",
            "no",
            "0",
            "off",
            "none",
            "null",
        }

    if isinstance(value, (int, float)):
        return value != 0

    return bool(value)


def _to_float(value: Any, field_name: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be numeric") from exc

    return result


def _list_from_context(value: Any) -> List[Any]:
    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


def _containers(request: Dict[str, Any], raw_order: Dict[str, Any]) -> List[Dict[str, Any]]:
    containers: List[Dict[str, Any]] = [
        request,
        raw_order,
    ]

    request_metadata = request.get("metadata")
    if isinstance(request_metadata, dict):
        containers.append(request_metadata)

    raw_order_metadata = raw_order.get("metadata")
    if isinstance(raw_order_metadata, dict):
        containers.append(raw_order_metadata)

    return containers


def _build_order_key(raw_order: Dict[str, Any]) -> str:
    asset_class = str(raw_order.get("asset_class", "")).strip().lower()
    symbol = str(raw_order.get("symbol", "")).strip().upper()
    side = str(raw_order.get("side", "")).strip().lower()
    order_type = str(raw_order.get("order_type", "")).strip().lower()
    correlation_id = str(raw_order.get("correlation_id", "")).strip()

    return f"{asset_class}:{symbol}:{side}:{order_type}:{correlation_id}"


def _denied_response(rule: str, field: str, message: str) -> Dict[str, Any]:
    return {
        "ok": False,
        "guardian": GUARDIAN_NAME,
        "guardian_version": GUARDIAN_VERSION,
        "decision": DECISION_DENIED,
        "error": {
            "type": ERROR_TYPE_RISK_DENY,
            "message": message,
        },
        "data": None,
        "risk_violation": {
            "rule": rule,
            "field": field,
            "message": message,
        },
        "safe_boundary": dict(SAFE_BOUNDARY),
    }


def _allowed_response(
    raw_order: Dict[str, Any],
    risk_context: Dict[str, Any],
    quantity: Optional[float],
    price: Optional[float],
    notional: Optional[float],
) -> Dict[str, Any]:
    return {
        "ok": True,
        "guardian": GUARDIAN_NAME,
        "guardian_version": GUARDIAN_VERSION,
        "decision": DECISION_ALLOWED,
        "error": None,
        "data": {
            "risk_allowed": True,
            "checked_rules": list(RISK_RULES),
            "order_key": _build_order_key(raw_order),
            "order_summary": {
                "asset_class": raw_order.get("asset_class"),
                "symbol": raw_order.get("symbol"),
                "side": raw_order.get("side"),
                "order_type": raw_order.get("order_type"),
                "quantity": quantity,
                "price": price,
                "notional": notional,
            },
            "risk_context_summary": {
                "max_quantity": risk_context.get("max_quantity"),
                "max_notional": risk_context.get("max_notional"),
                "blocked_symbols": _list_from_context(risk_context.get("blocked_symbols")),
                "blocked_asset_classes": _list_from_context(
                    risk_context.get("blocked_asset_classes")
                ),
                "duplicate_order_keys_count": len(
                    _list_from_context(risk_context.get("duplicate_order_keys"))
                ),
                "high_risk_flags_count": len(
                    _list_from_context(risk_context.get("high_risk_flags"))
                ),
            },
            "safe_boundary": dict(SAFE_BOUNDARY),
        },
    }


def _risk_context_or_deny(request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    risk_context = request.get("risk_context")

    if isinstance(risk_context, dict):
        return risk_context

    if _truthy(request.get("allow_missing_risk_context")):
        return {
            "allow_missing_risk_context": True,
        }

    return None


def _has_any_requested_field(containers: List[Dict[str, Any]], fields: set) -> Optional[str]:
    for container in containers:
        for field in fields:
            if field in container and _requested(container.get(field)):
                return field

    return None


def evaluate_paper_execution_risk(request: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(request, dict):
        return _denied_response(
            rule="request_must_be_dict",
            field="request",
            message="risk request must be a dict",
        )

    raw_order = request.get("raw_order")
    if not isinstance(raw_order, dict):
        return _denied_response(
            rule="raw_order_must_be_dict",
            field="raw_order",
            message="raw_order must be provided as object",
        )

    risk_context = _risk_context_or_deny(request)
    if risk_context is None:
        return _denied_response(
            rule="missing_risk_context",
            field="risk_context",
            message="risk_context is required before paper sandbox execution",
        )

    symbol = str(raw_order.get("symbol", "")).strip().upper()
    asset_class = str(raw_order.get("asset_class", "")).strip().lower()

    blocked_symbols = {
        str(item).strip().upper()
        for item in _list_from_context(risk_context.get("blocked_symbols"))
    }
    if symbol and symbol in blocked_symbols:
        return _denied_response(
            rule="blocked_symbol",
            field="symbol",
            message=f"symbol {symbol} is blocked by paper sandbox risk guardian",
        )

    blocked_asset_classes = {
        str(item).strip().lower()
        for item in _list_from_context(risk_context.get("blocked_asset_classes"))
    }
    if asset_class and asset_class in blocked_asset_classes:
        return _denied_response(
            rule="blocked_asset_class",
            field="asset_class",
            message=f"asset_class {asset_class} is blocked by paper sandbox risk guardian",
        )

    high_risk_flags = [
        item
        for item in _list_from_context(risk_context.get("high_risk_flags"))
        if str(item).strip()
    ]
    if high_risk_flags:
        return _denied_response(
            rule="high_risk_flags",
            field="high_risk_flags",
            message="high risk flags present in paper sandbox risk context",
        )

    containers = _containers(request, raw_order)

    leverage_field = _has_any_requested_field(containers, LEVERAGE_FIELDS)
    if leverage_field and not _truthy(risk_context.get("allow_leverage")):
        return _denied_response(
            rule="leverage_requested",
            field=leverage_field,
            message="leverage is not allowed in paper sandbox risk context",
        )

    margin_field = _has_any_requested_field(containers, MARGIN_FIELDS)
    if margin_field and not _truthy(risk_context.get("allow_margin")):
        return _denied_response(
            rule="margin_requested",
            field=margin_field,
            message="margin is not allowed in paper sandbox risk context",
        )

    try:
        quantity = _to_float(raw_order.get("quantity"), "quantity")
    except ValueError as exc:
        return _denied_response(
            rule="invalid_quantity",
            field="quantity",
            message=str(exc),
        )

    max_quantity = risk_context.get("max_quantity")
    if max_quantity is not None:
        max_quantity_float = _to_float(max_quantity, "max_quantity")
        if quantity > max_quantity_float:
            return _denied_response(
                rule="max_quantity",
                field="quantity",
                message="quantity exceeds paper sandbox max_quantity",
            )

    price_value = raw_order.get("price")
    if price_value is None:
        price_value = request.get("fill_price")

    price: Optional[float] = None
    notional: Optional[float] = None

    if price_value is not None:
        try:
            price = _to_float(price_value, "price")
            notional = quantity * price
        except ValueError as exc:
            return _denied_response(
                rule="invalid_price",
                field="price",
                message=str(exc),
            )

    max_notional = risk_context.get("max_notional")
    if max_notional is not None:
        if notional is None:
            return _denied_response(
                rule="max_notional",
                field="price",
                message="price is required when max_notional risk rule is enabled",
            )

        max_notional_float = _to_float(max_notional, "max_notional")
        if notional > max_notional_float:
            return _denied_response(
                rule="max_notional",
                field="notional",
                message="notional exceeds paper sandbox max_notional",
            )

    order_key = _build_order_key(raw_order)
    duplicate_order_keys = {
        str(item).strip().lower()
        for item in _list_from_context(risk_context.get("duplicate_order_keys"))
    }
    if order_key.lower() in duplicate_order_keys:
        return _denied_response(
            rule="duplicate_order_key",
            field="order_key",
            message="duplicate paper sandbox order key detected",
        )

    return _allowed_response(
        raw_order=raw_order,
        risk_context=risk_context,
        quantity=quantity,
        price=price,
        notional=notional,
    )
