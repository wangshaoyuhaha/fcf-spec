from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class BTCMarketContext:
    symbol: str
    exchange: str
    market_type: str
    timestamp: str
    timeframe: str

    open: float
    high: float
    low: float
    close: float
    last_price: float
    mark_price: Optional[float] = None
    index_price: Optional[float] = None

    volume: float = 0.0
    quote_volume: float = 0.0
    taker_buy_volume: float = 0.0
    taker_sell_volume: float = 0.0
    volume_change_rate: float = 0.0

    best_bid: Optional[float] = None
    best_ask: Optional[float] = None
    spread: Optional[float] = None
    bid_depth: Optional[float] = None
    ask_depth: Optional[float] = None
    orderbook_imbalance: Optional[float] = None

    funding_rate: Optional[float] = None
    next_funding_time: Optional[str] = None
    open_interest: Optional[float] = None
    open_interest_change_rate: Optional[float] = None
    long_short_ratio: Optional[float] = None

    realized_volatility: Optional[float] = None
    atr: Optional[float] = None
    price_change_1m: Optional[float] = None
    price_change_5m: Optional[float] = None
    price_change_15m: Optional[float] = None
    volatility_regime: str = "unknown"

    trend_direction: str = "unknown"
    regime_label: str = "unknown"
    momentum_score: Optional[float] = None
    mean_reversion_score: Optional[float] = None
    liquidity_level: str = "unknown"
    abnormal_move_detected: bool = False

    data_quality_level: str = "unknown"
    market_liquidity_risk: str = "unknown"
    volatility_risk: str = "unknown"
    slippage_risk: str = "unknown"
    funding_risk: str = "unknown"
    position_risk: str = "unknown"
    max_loss_risk: str = "unknown"

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "exchange": self.exchange,
            "market_type": self.market_type,
            "timestamp": self.timestamp,
            "timeframe": self.timeframe,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "last_price": self.last_price,
            "mark_price": self.mark_price,
            "index_price": self.index_price,
            "volume": self.volume,
            "quote_volume": self.quote_volume,
            "taker_buy_volume": self.taker_buy_volume,
            "taker_sell_volume": self.taker_sell_volume,
            "volume_change_rate": self.volume_change_rate,
            "best_bid": self.best_bid,
            "best_ask": self.best_ask,
            "spread": self.spread,
            "bid_depth": self.bid_depth,
            "ask_depth": self.ask_depth,
            "orderbook_imbalance": self.orderbook_imbalance,
            "funding_rate": self.funding_rate,
            "next_funding_time": self.next_funding_time,
            "open_interest": self.open_interest,
            "open_interest_change_rate": self.open_interest_change_rate,
            "long_short_ratio": self.long_short_ratio,
            "realized_volatility": self.realized_volatility,
            "atr": self.atr,
            "price_change_1m": self.price_change_1m,
            "price_change_5m": self.price_change_5m,
            "price_change_15m": self.price_change_15m,
            "volatility_regime": self.volatility_regime,
            "trend_direction": self.trend_direction,
            "regime_label": self.regime_label,
            "momentum_score": self.momentum_score,
            "mean_reversion_score": self.mean_reversion_score,
            "liquidity_level": self.liquidity_level,
            "abnormal_move_detected": self.abnormal_move_detected,
            "data_quality_level": self.data_quality_level,
            "market_liquidity_risk": self.market_liquidity_risk,
            "volatility_risk": self.volatility_risk,
            "slippage_risk": self.slippage_risk,
            "funding_risk": self.funding_risk,
            "position_risk": self.position_risk,
            "max_loss_risk": self.max_loss_risk,
            "metadata": self.metadata,
        }


def market_context_from_dict(data: Dict[str, Any]) -> BTCMarketContext:
    return BTCMarketContext(
        symbol=data["symbol"],
        exchange=data["exchange"],
        market_type=data["market_type"],
        timestamp=data["timestamp"],
        timeframe=data["timeframe"],
        open=data["open"],
        high=data["high"],
        low=data["low"],
        close=data["close"],
        last_price=data["last_price"],
        mark_price=data.get("mark_price"),
        index_price=data.get("index_price"),
        volume=data.get("volume", 0.0),
        quote_volume=data.get("quote_volume", 0.0),
        taker_buy_volume=data.get("taker_buy_volume", 0.0),
        taker_sell_volume=data.get("taker_sell_volume", 0.0),
        volume_change_rate=data.get("volume_change_rate", 0.0),
        best_bid=data.get("best_bid"),
        best_ask=data.get("best_ask"),
        spread=data.get("spread"),
        bid_depth=data.get("bid_depth"),
        ask_depth=data.get("ask_depth"),
        orderbook_imbalance=data.get("orderbook_imbalance"),
        funding_rate=data.get("funding_rate"),
        next_funding_time=data.get("next_funding_time"),
        open_interest=data.get("open_interest"),
        open_interest_change_rate=data.get("open_interest_change_rate"),
        long_short_ratio=data.get("long_short_ratio"),
        realized_volatility=data.get("realized_volatility"),
        atr=data.get("atr"),
        price_change_1m=data.get("price_change_1m"),
        price_change_5m=data.get("price_change_5m"),
        price_change_15m=data.get("price_change_15m"),
        volatility_regime=data.get("volatility_regime", "unknown"),
        trend_direction=data.get("trend_direction", "unknown"),
        regime_label=data.get("regime_label", "unknown"),
        momentum_score=data.get("momentum_score"),
        mean_reversion_score=data.get("mean_reversion_score"),
        liquidity_level=data.get("liquidity_level", "unknown"),
        abnormal_move_detected=data.get("abnormal_move_detected", False),
        data_quality_level=data.get("data_quality_level", "unknown"),
        market_liquidity_risk=data.get("market_liquidity_risk", "unknown"),
        volatility_risk=data.get("volatility_risk", "unknown"),
        slippage_risk=data.get("slippage_risk", "unknown"),
        funding_risk=data.get("funding_risk", "unknown"),
        position_risk=data.get("position_risk", "unknown"),
        max_loss_risk=data.get("max_loss_risk", "unknown"),
        metadata=data.get("metadata", {}),
    )
