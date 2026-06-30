from fcf.contracts.event import FCFEvent, create_event


class StrategyProposer:
    def propose(self, regime_event: FCFEvent) -> FCFEvent:
        return create_event(
            event_name="fcf.decision.proposed",
            source_module="strategy_proposer",
            correlation_id=regime_event.correlation_id,
            causation_id=regime_event.event_id,
            payload={
                "proposal_id": "demo_proposal",
                "target_id": regime_event.payload.get("target_id", "demo_target"),
                "direction": "observe_only",
                "confidence": regime_event.payload.get("confidence", 1.0),
                "suggested_stake": 0.0,
            },
        )
