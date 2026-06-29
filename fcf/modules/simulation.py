from fcf.core.event_model import Event


async def handle_decision_proposal(event, bus):
    proposal = event.payload
    allocation = proposal["params"]["allocation_pct"]
    risk = 0.14 if allocation <= 0.05 else 0.45

    await bus.publish(Event(
        event_type="fcf.simulation.completed",
        producer="fcf.modules.simulation",
        correlation_id=event.correlation_id,
        payload={
            "contract_version": "1.0",
            "proposal_id": proposal["proposal_id"],
            "simulation_pass": risk < 0.30,
            "metrics": {
                "tail_risk_score": risk,
                "expected_max_drawdown": 0.018,
                "stop_loss_hit_probability": 0.22,
            },
            "audit_reason": "Mock simulation: risk within Phase 1 policy limits.",
            "proposal": proposal,
        },
    ))
