from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from fcf.contracts.market_constants import (
    normalize_asset_class,
    normalize_market_type,
)


@dataclass(frozen=True)
class BaseMarketContext:
    asset_class: str
    symbol: str
    venue: str
    market_type: str
    timestamp: str
    timeframe: str

    currency: Optional[str] = None
    quote_currency: Optional[str] = None

    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    last_price: Optional[float] = None
    reference_price: Optional[float] = None
    settlement_price: Optional[float] = None

    volume: Optional[float] = None
    quote_volume: Optional[float] = None
    best_bid: Optional[float] = None
    best_ask: Optional[float] = None
    spread: Optional[float] = None
    bid_depth: Optional[float] = None
    ask_depth: Optional[float] = None
    liquidity_level: str = "unknown"

    realized_volatility: Optional[float] = None
    implied_volatility: Optional[float] = None
    atr: Optional[float] = None
    price_change_1m: Optional[float] = None
    price_change_5m: Optional[float] = None
    price_change_15m: Optional[float] = None
    price_change_1h: Optional[float] = None
    volatility_regime: str = "unknown"

    trend_direction: str = "unknown"
    regime_label: str = "unknown"
    momentum_score: Optional[float] = None
    mean_reversion_score: Optional[float] = None
    abnormal_move_detected: bool = False

    data_quality_level: str = "unknown"
    market_liquidity_risk: str = "unknown"
    volatility_risk: str = "unknown"
    slippage_risk: str = "unknown"
    position_risk: str = "unknown"
    max_loss_risk: str = "unknown"

    metadata: Dict[str, Any] = field(default_factory=dict)

    def normalized_asset_class(self) -> str:
        return normalize_asset_class(self.asset_class)

    def normalized_market_type(self) -> str:
        return normalize_market_type(self.market_type)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_class": self.normalized_asset_class(),
            "symbol": self.symbol,
            "venue": self.venue,
            "market_type": self.normalized_market_type(),
            "timestamp": self.timestamp,
            "timeframe": self.timeframe,
            "currency": self.currency,
            "quote_currency": self.quote_currency,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "last_price": self.last_price,
            "reference_price": self.reference_price,
            "settlement_price": self.settlement_price,
            "volume": self.volume,
            "quote_volume": self.quote_volume,
            "best_bid": self.best_bid,
            "best_ask": self.best_ask,
            "spread": self.spread,
            "bid_depth": self.bid_depth,
            "ask_depth": self.ask_depth,
            "liquidity_level": self.liquidity_level,
            "realized_volatility": self.realized_volatility,
            "implied_volatility": self.implied_volatility,
            "atr": self.atr,
            "price_change_1m": self.price_change_1m,
            "price_change_5m": self.price_change_5m,
            "price_change_15m": self.price_change_15m,
            "price_change_1h": self.price_change_1h,
            "volatility_regime": self.volatility_regime,
            "trend_direction": self.trend_direction,
            "regime_label": self.regime_label,
            "momentum_score": self.momentum_score,
            "mean_reversion_score": self.mean_reversion_score,
            "abnormal_move_detected": self.abnormal_move_detected,
            "data_quality_level": self.data_quality_level,
            "market_liquidity_risk": self.market_liquidity_risk,
            "volatility_risk": self.volatility_risk,
            "slippage_risk": self.slippage_risk,
            "position_risk": self.position_risk,
            "max_loss_risk": self.max_loss_risk,
            "metadata": self.metadata,
        }


def base_market_context_from_dict(data: Dict[str, Any]) -> BaseMarketContext:
    return BaseMarketContext(
        asset_class=normalize_asset_class(data.get("asset_class")),
        symbol=data["symbol"],
        venue=data["venue"],
        market_type=normalize_market_type(data.get("market_type")),
        timestamp=data["timestamp"],
        timeframe=data["timeframe"],
        currency=data.get("currency"),
        quote_currency=data.get("quote_currency"),
        open=data.get("open"),
        high=data.get("high"),
        low=data.get("low"),
        close=data.get("close"),
        last_price=data.get("last_price"),
        reference_price=data.get("reference_price"),
        settlement_price=data.get("settlement_price"),
        volume=data.get("volume"),
        quote_volume=data.get("quote_volume"),
        best_bid=data.get("best_bid"),
        best_ask=data.get("best_ask"),
        spread=data.get("spread"),
        bid_depth=data.get("bid_depth"),
        ask_depth=data.get("ask_depth"),
        liquidity_level=data.get("liquidity_level", "unknown"),
        realized_volatility=data.get("realized_volatility"),
        implied_volatility=data.get("implied_volatility"),
        atr=data.get("atr"),
        price_change_1m=data.get("price_change_1m"),
        price_change_5m=data.get("price_change_5m"),
        price_change_15m=data.get("price_change_15m"),
        price_change_1h=data.get("price_change_1h"),
        volatility_regime=data.get("volatility_regime", "unknown"),
        trend_direction=data.get("trend_direction", "unknown"),
        regime_label=data.get("regime_label", "unknown"),
        momentum_score=data.get("momentum_score"),
        mean_reversion_score=data.get("mean_reversion_score"),
        abnormal_move_detected=data.get("abnormal_move_detected", False),
        data_quality_level=data.get("data_quality_level", "unknown"),
        market_liquidity_risk=data.get("market_liquidity_risk", "unknown"),
        volatility_risk=data.get("volatility_risk", "unknown"),
        slippage_risk=data.get("slippage_risk", "unknown"),
        position_risk=data.get("position_risk", "unknown"),
        max_loss_risk=data.get("max_loss_risk", "unknown"),
        metadata=data.get("metadata", {}),
    )
