from typing import Any, Dict, Optional

from fcf.contracts.base_market_context import BaseMarketContext
from fcf.contracts.market_context import BTCMarketContext


def _infer_crypto_currencies(symbol: str) -> Dict[str, Optional[str]]:
    upper_symbol = symbol.upper()

    known_quotes = [
        "USDT",
        "USDC",
        "USD",
        "BTC",
        "ETH",
        "EUR",
        "JPY",
    ]

    for quote in known_quotes:
        if upper_symbol.endswith(quote) and len(upper_symbol) > len(quote):
            return {
                "currency": upper_symbol[: -len(quote)],
                "quote_currency": quote,
            }

    return {
        "currency": None,
        "quote_currency": None,
    }


def btc_market_context_to_base(
    context: BTCMarketContext,
    venue: Optional[str] = None,
) -> BaseMarketContext:
    currencies = _infer_crypto_currencies(context.symbol)

    return BaseMarketContext(
        asset_class="crypto",
        symbol=context.symbol,
        venue=venue or context.exchange,
        market_type=context.market_type,
        timestamp=context.timestamp,
        timeframe=context.timeframe,
        currency=currencies["currency"],
        quote_currency=currencies["quote_currency"],
        open=context.open,
        high=context.high,
        low=context.low,
        close=context.close,
        last_price=context.last_price,
        reference_price=context.index_price,
        settlement_price=context.mark_price,
        volume=context.volume,
        quote_volume=context.quote_volume,
        best_bid=context.best_bid,
        best_ask=context.best_ask,
        spread=context.spread,
        bid_depth=context.bid_depth,
        ask_depth=context.ask_depth,
        liquidity_level=context.liquidity_level,
        realized_volatility=context.realized_volatility,
        implied_volatility=None,
        atr=context.atr,
        price_change_1m=context.price_change_1m,
        price_change_5m=context.price_change_5m,
        price_change_15m=context.price_change_15m,
        price_change_1h=None,
        volatility_regime=context.volatility_regime,
        trend_direction=context.trend_direction,
        regime_label=context.regime_label,
        momentum_score=context.momentum_score,
        mean_reversion_score=context.mean_reversion_score,
        abnormal_move_detected=context.abnormal_move_detected,
        data_quality_level=context.data_quality_level,
        market_liquidity_risk=context.market_liquidity_risk,
        volatility_risk=context.volatility_risk,
        slippage_risk=context.slippage_risk,
        position_risk=context.position_risk,
        max_loss_risk=context.max_loss_risk,
        metadata={
            "adapter": "btc_market_context_to_base",
            "source_context_type": "BTCMarketContext",
            "source_exchange": context.exchange,
            "source_metadata": context.metadata,
        },
    )


def btc_market_context_to_event_payload(
    context: BTCMarketContext,
    venue: Optional[str] = None,
) -> Dict[str, Any]:
    base_context = btc_market_context_to_base(context, venue=venue)

    return {
        "asset_class": base_context.normalized_asset_class(),
        "context_type": "BaseMarketContext",
        "source_context_type": "BTCMarketContext",
        "base_market_context": base_context.to_dict(),
        "source_market_context": context.to_dict(),
    }
