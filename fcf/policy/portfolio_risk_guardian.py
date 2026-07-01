from collections import Counter
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Set


GUARDIAN_NAME = "portfolio_risk_guardian"
GUARDIAN_VERSION = "0.1.0"


def _normalize_asset_class(value: Any) -> str:
    return str(value or "").strip().lower()


def _normalize_symbol(value: Any) -> str:
    return str(value or "").strip().lower()


def _normalize_side(value: Any) -> str:
    return str(value or "").strip().lower()


def _normalize_order_key(order: Dict[str, Any]) -> str:
    raw_order = order.get("raw_order") or {}
    return str(
        order.get("order_id")
        or raw_order.get("correlation_id")
        or raw_order.get("symbol")
        or ""
    ).strip().lower()


def _to_decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")


def _order_notional(order: Dict[str, Any]) -> Decimal:
    raw_order = order.get("raw_order") or {}
    quantity = _to_decimal(raw_order.get("quantity"))
    price = _to_decimal(raw_order.get("price"))
    return abs(quantity * price)


def _safe_boundary() -> Dict[str, Any]:
    return {
        "execution_mode": "paper",
        "real_order": False,
        "real_execution": False,
        "real_exchange_api": False,
        "real_money_impact": False,
        "no_real_exchange_api": True,
        "no_real_order_placement": True,
        "no_exchange_api_key_storage": True,
        "no_wallet_private_key_access": True,
        "policy_risk_cannot_be_bypassed": True,
        "portfolio_risk_deny_is_not_exchange_reject": True,
    }


def _duplicates(values: List[str]) -> List[str]:
    counter = Counter(value for value in values if value)
    return sorted(value for value, count in counter.items() if count > 1)


def _asset_class_counts(orders: List[Dict[str, Any]]) -> Dict[str, int]:
    counter = Counter(
        _normalize_asset_class((order.get("raw_order") or {}).get("asset_class"))
        for order in orders
    )
    return dict(sorted(counter.items()))


def _side_counts(orders: List[Dict[str, Any]]) -> Dict[str, int]:
    counter = Counter(
        _normalize_side((order.get("raw_order") or {}).get("side"))
        for order in orders
    )
    return dict(sorted(counter.items()))


def _notional_by_asset_class_decimal(orders: List[Dict[str, Any]]) -> Dict[str, Decimal]:
    totals: Dict[str, Decimal] = {}

    for order in orders:
        asset_class = _normalize_asset_class((order.get("raw_order") or {}).get("asset_class"))
        totals[asset_class] = totals.get(asset_class, Decimal("0")) + _order_notional(order)

    return dict(sorted(totals.items()))


def _build_exposure(
    orders: List[Dict[str, Any]],
    risk_context: Dict[str, Any],
) -> Dict[str, Any]:
    symbols = [
        _normalize_symbol((order.get("raw_order") or {}).get("symbol"))
        for order in orders
    ]
    asset_classes = [
        _normalize_asset_class((order.get("raw_order") or {}).get("asset_class"))
        for order in orders
    ]
    order_keys = [_normalize_order_key(order) for order in orders]

    blocked_symbols = {
        _normalize_symbol(symbol)
        for symbol in risk_context.get("blocked_symbols", [])
    }
    blocked_asset_classes = {
        _normalize_asset_class(asset_class)
        for asset_class in risk_context.get("blocked_asset_classes", [])
    }

    notional_by_asset_decimal = _notional_by_asset_class_decimal(orders)
    notionals = [_order_notional(order) for order in orders]

    return {
        "order_count": len(orders),
        "total_notional": float(sum(notionals, Decimal("0"))),
        "notional_by_asset_class": {
            asset_class: float(notional)
            for asset_class, notional in notional_by_asset_decimal.items()
        },
        "order_count_by_asset_class": _asset_class_counts(orders),
        "side_count_by_asset_class": _side_counts(orders),
        "symbols": sorted(set(symbols)),
        "duplicated_symbols": _duplicates(symbols),
        "duplicated_order_keys": _duplicates(order_keys),
        "blocked_symbols_hit": sorted(blocked_symbols.intersection(symbols)),
        "blocked_asset_classes_hit": sorted(blocked_asset_classes.intersection(asset_classes)),
        "max_single_order_notional": float(max(notionals) if notionals else Decimal("0")),
    }


def evaluate_portfolio_risk_guardian(
    *,
    orders: List[Dict[str, Any]],
    risk_context: Dict[str, Any],
) -> Dict[str, Any]:
    if not isinstance(orders, list):
        return {
            "ok": False,
            "guardian": GUARDIAN_NAME,
            "guardian_version": GUARDIAN_VERSION,
            "deny_reasons": ["orders_must_be_list"],
            "checks": {},
            "exposure": {},
            "safe_boundary": _safe_boundary(),
        }

    if not isinstance(risk_context, dict):
        risk_context = {}

    exposure = _build_exposure(orders=orders, risk_context=risk_context)
    deny_reasons: List[str] = []
    checks: Dict[str, Any] = {}

    max_order_count = risk_context.get("max_order_count")
    checks["max_order_count"] = {
        "configured": max_order_count,
        "actual": len(orders),
        "passed": not isinstance(max_order_count, int) or len(orders) <= max_order_count,
    }
    if checks["max_order_count"]["passed"] is False:
        deny_reasons.append("max_order_count_exceeded")

    max_total_notional = risk_context.get("max_total_notional")
    total_notional = _to_decimal(exposure["total_notional"])
    checks["max_total_notional"] = {
        "configured": max_total_notional,
        "actual": float(total_notional),
        "passed": max_total_notional is None or total_notional <= _to_decimal(max_total_notional),
    }
    if checks["max_total_notional"]["passed"] is False:
        deny_reasons.append("max_total_notional_exceeded")

    max_asset_class_notional = risk_context.get("max_asset_class_notional") or {}
    max_asset_class_passed = True
    max_asset_class_hits: List[str] = []
    if isinstance(max_asset_class_notional, dict):
        for asset_class, notional in exposure["notional_by_asset_class"].items():
            limit = max_asset_class_notional.get(asset_class)
            if limit is not None and _to_decimal(notional) > _to_decimal(limit):
                max_asset_class_passed = False
                max_asset_class_hits.append(asset_class)

    checks["max_asset_class_notional"] = {
        "configured": max_asset_class_notional,
        "hits": sorted(max_asset_class_hits),
        "passed": max_asset_class_passed,
    }
    if max_asset_class_passed is False:
        deny_reasons.append("max_asset_class_notional_exceeded")

    checks["blocked_asset_classes"] = {
        "configured": sorted(
            _normalize_asset_class(item)
            for item in risk_context.get("blocked_asset_classes", [])
        ),
        "hits": exposure["blocked_asset_classes_hit"],
        "passed": exposure["blocked_asset_classes_hit"] == [],
    }
    if checks["blocked_asset_classes"]["passed"] is False:
        deny_reasons.append("blocked_asset_class")

    checks["blocked_symbols"] = {
        "configured": sorted(
            _normalize_symbol(item)
            for item in risk_context.get("blocked_symbols", [])
        ),
        "hits": exposure["blocked_symbols_hit"],
        "passed": exposure["blocked_symbols_hit"] == [],
    }
    if checks["blocked_symbols"]["passed"] is False:
        deny_reasons.append("blocked_symbol")

    configured_duplicate_order_keys: Set[str] = {
        _normalize_symbol(item)
        for item in risk_context.get("duplicate_order_keys", [])
    }
    actual_order_keys = {
        _normalize_order_key(order)
        for order in orders
    }
    duplicate_order_key_hits = sorted(
        configured_duplicate_order_keys.intersection(actual_order_keys)
    )
    all_duplicate_order_keys = sorted(
        set(exposure["duplicated_order_keys"]).union(duplicate_order_key_hits)
    )
    checks["duplicate_order_keys"] = {
        "configured_hits": duplicate_order_key_hits,
        "actual_duplicates": exposure["duplicated_order_keys"],
        "hits": all_duplicate_order_keys,
        "passed": all_duplicate_order_keys == [],
    }
    if checks["duplicate_order_keys"]["passed"] is False:
        deny_reasons.append("duplicate_order_key")

    max_same_side_count = risk_context.get("max_same_side_count")
    side_counts = exposure["side_count_by_asset_class"]
    max_same_side_passed = (
        not isinstance(max_same_side_count, int)
        or all(count <= max_same_side_count for count in side_counts.values())
    )
    checks["max_same_side_count"] = {
        "configured": max_same_side_count,
        "actual": side_counts,
        "passed": max_same_side_passed,
    }
    if max_same_side_passed is False:
        deny_reasons.append("max_same_side_count_exceeded")

    max_single_order_notional = risk_context.get("max_single_order_notional")
    max_single_order_notional_actual = _to_decimal(exposure["max_single_order_notional"])
    max_single_order_passed = (
        max_single_order_notional is None
        or max_single_order_notional_actual <= _to_decimal(max_single_order_notional)
    )
    checks["max_single_order_notional"] = {
        "configured": max_single_order_notional,
        "actual": float(max_single_order_notional_actual),
        "passed": max_single_order_passed,
    }
    if max_single_order_passed is False:
        deny_reasons.append("max_single_order_notional_exceeded")

    return {
        "ok": len(deny_reasons) == 0,
        "guardian": GUARDIAN_NAME,
        "guardian_version": GUARDIAN_VERSION,
        "deny_reasons": deny_reasons,
        "checks": checks,
        "exposure": exposure,
        "safe_boundary": _safe_boundary(),
    }
