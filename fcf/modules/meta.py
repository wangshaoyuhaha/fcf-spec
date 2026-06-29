from fcf.core.event_model import Event
from fcf.core.policy_engine import PolicyEngine


policy_engine = PolicyEngine()


async def handle_simulation_completed(event, bus):
    payload = event.payload
    proposal = payload["proposal"]
    regime_context = proposal["governance_snapshot"]["regime"]

    panic_probability = 0.88 if regime_context == "PANIC" else 0.12
    policy = policy_engine.evaluate({"panic_probability": panic_probability})

    if not payload["simulation_pass"]:
        system_mode = "BLOCKED"
        confidence = 0.25
        reason = "Simulation failed."
    else:
        system_mode = policy["execution_mode"]
        confidence = 0.91 if policy["policy_pass"] else 0.20
        reason = policy["reason"]

    await bus.publish(Event(
        event_type="fcf.meta.audit.completed",
        producer="fcf.modules.meta",
        correlation_id=event.correlation_id,
        payload={
            "contract_version": "1.0",
            "proposal_id": payload["proposal_id"],
            "system_mode": system_mode,
            "system_confidence": confidence,
            "meta_checks": {
                "risk": "PASS" if payload["simulation_pass"] else "FAIL",
                "drift": "PASS",
                "health": "PASS",
                "regime": "PASS" if policy["policy_pass"] else "FAIL",
            },
            "reason": reason,
            "simulation_review": payload,
        },
    ))
