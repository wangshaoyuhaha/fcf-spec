from fcf.core.event_model import Event


async def handle_fact_matrix(event, bus):
    ms = event.payload["market_state"]
    vol = ms["volatility_24h"]

    if vol >= 0.08:
        regime = "PANIC"
        panic_probability = 0.88
    elif vol >= 0.04:
        regime = "HIGH_VOLATILITY"
        panic_probability = 0.32
    else:
        regime = "TREND_UP" if ms["return_1h"] > 0 else "RANGE"
        panic_probability = 0.12

    await bus.publish(Event(
        event_type="fcf.regime.detected",
        producer="fcf.modules.regime",
        correlation_id=event.correlation_id,
        payload={
            "contract_version": "1.0",
            "asset": event.payload["asset"],
            "regime": regime,
            "regime_confidence": 0.81,
            "panic_probability": panic_probability,
            "method": "mock_threshold_v1",
            "source_fact_matrix": event.payload,
        },
    ))
