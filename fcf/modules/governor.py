from fcf.core.event_model import Event
import uuid


async def handle_cognitive_unit(event, bus):
    unit = event.payload
    proposal_id = f"prop_{uuid.uuid4().hex[:12]}"

    if unit["direction"] == "WAIT":
        action = "WAIT"
        allocation_pct = 0.0
    else:
        action = unit["direction"]
        allocation_pct = 0.05

    proposal = {
        "contract_version": "1.0",
        "proposal_id": proposal_id,
        "asset": "BTC",
        "action": action,
        "params": {
            "entry_range": [94800.0, 95000.0],
            "stop_loss": unit["invalid_level"],
            "take_profit": unit["target_level"],
            "allocation_pct": allocation_pct,
        },
        "governance_snapshot": {
            "regime": unit["regime_context"]["regime"],
            "allocated_weights": {"smc_mock_unit": 1.0},
            "aggregated_confidence": unit["confidence"],
            "reason": unit["reason"],
        },
    }

    await bus.publish(Event(
        event_type="fcf.decision.proposal.created",
        producer="fcf.modules.governor",
        correlation_id=event.correlation_id,
        payload=proposal,
    ))
