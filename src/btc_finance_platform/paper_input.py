from typing import Any


def validate_paper_input(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")

    symbol = payload.get("symbol")
    price = payload.get("price")
    reference_price = payload.get("reference_price", price)

    if not symbol or not isinstance(symbol, str):
        raise ValueError("symbol is required")

    if price is None or float(price) <= 0:
        raise ValueError("price must be positive")

    if reference_price is None or float(reference_price) <= 0:
        raise ValueError("reference_price must be positive")

    return {
        "ok": True,
        "type": "validated_paper_input",
        "symbol": symbol.upper(),
        "price": float(price),
        "reference_price": float(reference_price),
        "paper_only": True,
        "real_exchange_api": False,
        "real_order": False,
        "operator_review_required": True,
    }
