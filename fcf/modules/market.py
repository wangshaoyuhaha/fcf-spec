from fcf.core.event_model import Event


async def emit_mock_market(bus, correlation_id: str):
    event = Event(
        event_type="fcf.market.snapshot.emitted",
        producer="fcf.modules.market",
        correlation_id=correlation_id,
        payload={
            "contract_version": "1.0",
            "asset": "BTC",
            "price": 95000.0,
            "return_1h": 0.012,
            "volatility_24h": 0.038,
            "funding_rate": -0.0001,
            "open_interest_change_pct": 0.03,
        },
    )
    await bus.publish(event)
