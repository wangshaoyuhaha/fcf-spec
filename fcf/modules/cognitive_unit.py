from fcf.core.event_model import Event


async def handle_regime_detected(event, bus):
    regime = event.payload["regime"]
    if regime in ["PANIC", "HIGH_VOLATILITY"]:
        direction = "WAIT"
        confidence = 0.70
        risk_score = 0.75
        reason = "High volatility regime detected; avoid aggressive exposure."
    else:
        direction = "LONG"
        confidence = 0.72
        risk_score = 0.38
        reason = "Mock SMC unit: price swept liquidity and returned to demand zone."

    await bus.publish(Event(
        event_type="fcf.cognitive_unit.completed",
        producer="fcf.modules.cognitive_unit.smc_mock",
        correlation_id=event.correlation_id,
        payload={
            "contract_version": "1.0",
            "unit_id": "smc_mock_unit",
            "direction": direction,
            "confidence": confidence,
            "risk_score": risk_score,
            "reason": reason,
            "invalid_level": 93000.0,
            "target_level": 99000.0,
            "regime_context": event.payload,
        },
    ))
