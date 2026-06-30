from fcf.contracts.event import FCFEvent, create_event


class ShadowSimulator:
    def simulate(self, decision_event: FCFEvent) -> FCFEvent:
        return create_event(
            event_name="fcf.shadow.simulated",
            source_module="shadow_simulator",
            correlation_id=decision_event.correlation_id,
            causation_id=decision_event.event_id,
            payload={
                "proposal_id": decision_event.payload.get("proposal_id"),
                "simulated_price": 1.0,
                "simulated_stake": decision_event.payload.get("suggested_stake", 0.0),
                "simulated_slippage": 0.0,
                "simulation_result": "completed",
            },
        )
