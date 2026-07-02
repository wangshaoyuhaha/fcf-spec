from typing import Any


PAPER_ONLY_FLAGS = {
    "paper_only": True,
    "real_exchange_api": False,
    "real_api_key_required": False,
    "wallet_private_key_required": False,
    "real_order": False,
    "real_execution": False,
    "real_balance": False,
    "real_position": False,
    "real_money_impact": False,
    "operator_review_required": True,
}


def paper_flags() -> dict[str, Any]:
    return dict(PAPER_ONLY_FLAGS)


def _to_positive_float(value: Any, field_name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a positive number") from exc

    if number <= 0:
        raise ValueError(f"{field_name} must be a positive number")
    return number


def classify_deviation_magnitude(deviation_pct: float) -> str:
    value = abs(float(deviation_pct))
    if value < 0.005:
        return "tiny"
    if value < 0.02:
        return "small"
    if value < 0.05:
        return "medium"
    return "large"


def calculate_price_deviation(price: Any, reference_price: Any) -> dict[str, Any]:
    price_value = _to_positive_float(price, "price")
    reference_value = _to_positive_float(reference_price, "reference_price")
    deviation_abs = price_value - reference_value
    deviation_pct = deviation_abs / reference_value

    if deviation_pct > 0:
        direction = "above_reference"
    elif deviation_pct < 0:
        direction = "below_reference"
    else:
        direction = "at_reference"

    return {
        "ok": True,
        "type": "price_deviation_analysis",
        "price": price_value,
        "reference_price": reference_value,
        "deviation_abs": deviation_abs,
        "deviation_pct": deviation_pct,
        "direction": direction,
        "magnitude": classify_deviation_magnitude(deviation_pct),
        **paper_flags(),
    }


def calculate_simple_momentum(price_history: list[Any] | None) -> dict[str, Any]:
    if price_history is None or len(price_history) < 2:
        return {
            "ok": True,
            "type": "simple_momentum_analysis",
            "available": False,
            "momentum_pct": 0.0,
            "direction": "unknown",
            **paper_flags(),
        }

    values = [_to_positive_float(item, "price_history") for item in price_history]
    first = values[0]
    last = values[-1]
    momentum_pct = (last - first) / first

    if momentum_pct > 0:
        direction = "up"
    elif momentum_pct < 0:
        direction = "down"
    else:
        direction = "flat"

    return {
        "ok": True,
        "type": "simple_momentum_analysis",
        "available": True,
        "first_price": first,
        "last_price": last,
        "momentum_pct": momentum_pct,
        "direction": direction,
        **paper_flags(),
    }


def estimate_paper_risk_score(deviation_pct: float, momentum_pct: float = 0.0) -> dict[str, Any]:
    deviation_component = min(abs(float(deviation_pct)) * 1000, 70)
    momentum_component = min(abs(float(momentum_pct)) * 500, 30)
    score = round(deviation_component + momentum_component, 2)

    if score < 15:
        level = "low"
    elif score < 40:
        level = "medium"
    else:
        level = "high"

    return {
        "ok": True,
        "type": "paper_risk_score",
        "score": score,
        "level": level,
        "method": "rule_based_paper_only_baseline",
        **paper_flags(),
    }


def draft_paper_signal(
    symbol: str,
    price: Any,
    reference_price: Any,
    price_history: list[Any] | None = None,
) -> dict[str, Any]:
    if not symbol or not str(symbol).strip():
        raise ValueError("symbol is required")

    normalized_symbol = str(symbol).strip().upper()
    deviation = calculate_price_deviation(price, reference_price)
    momentum = calculate_simple_momentum(price_history)
    risk = estimate_paper_risk_score(
        deviation["deviation_pct"],
        momentum["momentum_pct"],
    )

    deviation_pct = deviation["deviation_pct"]
    momentum_pct = momentum["momentum_pct"]

    if risk["level"] == "high":
        signal = "paper_review_only_high_risk"
    elif deviation_pct > 0.01 and momentum_pct >= 0:
        signal = "paper_watch_upside_bias"
    elif deviation_pct < -0.01 and momentum_pct <= 0:
        signal = "paper_watch_downside_bias"
    else:
        signal = "paper_neutral_watch"

    return {
        "ok": True,
        "type": "paper_signal_draft",
        "symbol": normalized_symbol,
        "signal": signal,
        "deviation": deviation,
        "momentum": momentum,
        "risk": risk,
        "decision": "no_real_trade_paper_signal_only",
        **paper_flags(),
    }


def analyze_paper_item(item: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise ValueError("item must be a dict")

    return draft_paper_signal(
        symbol=item.get("symbol", ""),
        price=item.get("price"),
        reference_price=item.get("reference_price"),
        price_history=item.get("price_history"),
    )


def analyze_paper_batch(items: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if not items:
        raise ValueError("items must not be empty")

    analyses = [analyze_paper_item(item) for item in items]
    high_risk_count = sum(1 for item in analyses if item["risk"]["level"] == "high")

    return {
        "ok": True,
        "type": "paper_batch_analysis_baseline",
        "count": len(analyses),
        "symbols": [item["symbol"] for item in analyses],
        "high_risk_count": high_risk_count,
        "items": analyses,
        "decision": "batch_analysis_paper_only_no_real_trade",
        **paper_flags(),
    }
