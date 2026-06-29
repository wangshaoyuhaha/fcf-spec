from fcf.core.event_model import Event


async def handle_market_snapshot(event, bus):
    p = event.payload
    fact_matrix = {
        "contract_version": "1.0",
        "asset": p["asset"],
        "quality_score": 0.95,
        "market_state": {
            "price": p["price"],
            "return_1h": p["return_1h"],
            "volatility_24h": p["volatility_24h"],
            "funding_rate": p["funding_rate"],
            "oi_change_pct": p["open_interest_change_pct"],
        },
        "facts": [
            {"source": "market", "metric": "volatility", "status": "rising"},
            {"source": "derivatives", "metric": "open_interest", "status": "increasing"},
        ],
    }

    await bus.publish(Event(
        event_type="fcf.perception.fact_matrix.ready",
        producer="fcf.modules.perception",
        correlation_id=event.correlation_id,
        payload=fact_matrix,
    ))
