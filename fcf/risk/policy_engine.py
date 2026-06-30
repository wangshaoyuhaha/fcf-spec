from fcf.contracts.event import FCFEvent, create_event


class PolicyEngine:
    def review(self, decision_event: FCFEvent) -> FCFEvent:
        suggested_stake = decision_event.payload.get("suggested_stake", 0.0)

        if suggested_stake <= 0.0:
            review_result = "approved"
            risk_level = "low"
            approved_stake = 0.0
            reasons = []
        else:
            review_result = "shadow_only"
            risk_level = "medium"
            approved_stake = 0.0
            reasons = ["D9 minimal runtime does not allow real stake"]

        return create_event(
            event_name="fcf.policy.reviewed",
            source_module="policy_engine",
            correlation_id=decision_event.correlation_id,
            causation_id=decision_event.event_id,
            payload={
                "proposal_id": decision_event.payload.get("proposal_id"),
                "review_result": review_result,
                "risk_level": risk_level,
                "approved_stake": approved_stake,
                "reasons": reasons,
            },
        )
