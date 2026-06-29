from fcf.core.event_model import Event


async def handle_meta_audit(event, bus):
    meta = event.payload
    proposal = meta["simulation_review"]["proposal"]

    execution_order = {
        "contract_version": "1.0",
        "execution_mode": meta["system_mode"],
        "proposal_id": meta["proposal_id"],
        "order": {
            "asset": proposal["asset"],
            "action": "BUY" if proposal["action"] == "LONG" else proposal["action"],
            "order_type": "MARKET",
            "position_size_pct": proposal["params"]["allocation_pct"],
            "limit_price": proposal["params"]["entry_range"][1],
            "stop_loss": proposal["params"]["stop_loss"],
            "take_profit": proposal["params"]["take_profit"],
        },
        "meta_reason": meta["reason"],
    }

    await bus.publish(Event(
        event_type="fcf.execution.order.emitted",
        producer="fcf.modules.execution",
        correlation_id=event.correlation_id,
        payload=execution_order,
    ))

    await bus.publish(Event(
        event_type="fcf.execution.order.executed",
        producer="fcf.modules.execution.shadow_adapter",
        correlation_id=event.correlation_id,
        payload={
            "contract_version": "1.0",
            "proposal_id": meta["proposal_id"],
            "execution_mode": meta["system_mode"],
            "status": "RECORDED_ONLY",
            "message": "Phase 1: no real order sent. Shadow execution recorded.",
            "order": execution_order,
        },
    ))
