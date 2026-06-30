from typing import Any, Dict, Optional

from fcf.contracts.market_context import BTCMarketContext


def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _required_float(data: Dict[str, Any], key: str) -> float:
    value = _to_float(data.get(key))
    if value is None:
        raise ValueError(f"missing or invalid required numeric field: {key}")
    return value


def _calculate_spread(best_bid: Optional[float], best_ask: Optional[float]) -> Optional[float]:
    if best_bid is None or best_ask is None:
        return None
    return best_ask - best_bid


def _calculate_orderbook_imbalance(
    bid_depth: Optional[float],
    ask_depth: Optional[float],
) -> Optional[float]:
    if bid_depth is None or ask_depth is None:
        return None

    total_depth = bid_depth + ask_depth

    if total_depth == 0:
        return None

    return (bid_depth - ask_depth) / total_depth


def _detect_data_quality(data: Dict[str, Any]) -> str:
    required_fields = [
        "symbol",
        "exchange",
        "market_type",
        "timestamp",
        "timeframe",
        "open",
        "high",
        "low",
        "close",
        "last_price",
    ]

    for field_name in required_fields:
        if data.get(field_name) is None:
            return "bad"

    if _to_float(data.get("best_bid")) is None or _to_float(data.get("best_ask")) is None:
        return "partial"

    if _to_float(data.get("volume")) is None:
        return "partial"

    return "good"


def build_btc_market_context(raw: Dict[str, Any]) -> BTCMarketContext:
    best_bid = _to_float(raw.get("best_bid"))
    best_ask = _to_float(raw.get("best_ask"))
    bid_depth = _to_float(raw.get("bid_depth"))
    ask_depth = _to_float(raw.get("ask_depth"))

    spread = raw.get("spread")

    if spread is None:
        spread = _calculate_spread(best_bid, best_ask)
    else:
        spread = _to_float(spread)

    orderbook_imbalance = raw.get("orderbook_imbalance")

    if orderbook_imbalance is None:
        orderbook_imbalance = _calculate_orderbook_imbalance(bid_depth, ask_depth)
    else:
        orderbook_imbalance = _to_float(orderbook_imbalance)

    data_quality_level = raw.get("data_quality_level") or _detect_data_quality(raw)

    return BTCMarketContext(
        symbol=raw["symbol"],
        exchange=raw["exchange"],
        market_type=raw["market_type"],
        timestamp=raw["timestamp"],
        timeframe=raw["timeframe"],
        open=_required_float(raw, "open"),
        high=_required_float(raw, "high"),
        low=_required_float(raw, "low"),
        close=_required_float(raw, "close"),
        last_price=_required_float(raw, "last_price"),
        mark_price=_to_float(raw.get("mark_price")),
        index_price=_to_float(raw.get("index_price")),
        volume=_to_float(raw.get("volume")) or 0.0,
        quote_volume=_to_float(raw.get("quote_volume")) or 0.0,
        taker_buy_volume=_to_float(raw.get("taker_buy_volume")) or 0.0,
        taker_sell_volume=_to_float(raw.get("taker_sell_volume")) or 0.0,
        volume_change_rate=_to_float(raw.get("volume_change_rate")) or 0.0,
        best_bid=best_bid,
        best_ask=best_ask,
        spread=spread,
        bid_depth=bid_depth,
        ask_depth=ask_depth,
        orderbook_imbalance=orderbook_imbalance,
        funding_rate=_to_float(raw.get("funding_rate")),
        next_funding_time=raw.get("next_funding_time"),
        open_interest=_to_float(raw.get("open_interest")),
        open_interest_change_rate=_to_float(raw.get("open_interest_change_rate")),
        long_short_ratio=_to_float(raw.get("long_short_ratio")),
        realized_volatility=_to_float(raw.get("realized_volatility")),
        atr=_to_float(raw.get("atr")),
        price_change_1m=_to_float(raw.get("price_change_1m")),
        price_change_5m=_to_float(raw.get("price_change_5m")),
        price_change_15m=_to_float(raw.get("price_change_15m")),
        volatility_regime=raw.get("volatility_regime", "unknown"),
        trend_direction=raw.get("trend_direction", "unknown"),
        regime_label=raw.get("regime_label", "unknown"),
        momentum_score=_to_float(raw.get("momentum_score")),
        mean_reversion_score=_to_float(raw.get("mean_reversion_score")),
        liquidity_level=raw.get("liquidity_level", "unknown"),
        abnormal_move_detected=bool(raw.get("abnormal_move_detected", False)),
        data_quality_level=data_quality_level,
        market_liquidity_risk=raw.get("market_liquidity_risk", "unknown"),
        volatility_risk=raw.get("volatility_risk", "unknown"),
        slippage_risk=raw.get("slippage_risk", "unknown"),
        funding_risk=raw.get("funding_risk", "unknown"),
        position_risk=raw.get("position_risk", "unknown"),
        max_loss_risk=raw.get("max_loss_risk", "unknown"),
        metadata=raw.get("metadata", {}),
    )
