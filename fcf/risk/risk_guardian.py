from fcf.contracts.event import FCFEvent, create_event


class RiskGuardian:
    def approve(self, policy_event: FCFEvent) -> FCFEvent:
        review_result = policy_event.payload.get("review_result")

        if review_result != "approved":
            return create_event(
                event_name="fcf.risk.rejected",
                source_module="risk_guardian",
                correlation_id=policy_event.correlation_id,
                causation_id=policy_event.event_id,
                payload={
                    "proposal_id": policy_event.payload.get("proposal_id"),
                    "reason": "policy_not_approved",
                },
            )

        return create_event(
            event_name="fcf.order.approved",
            source_module="risk_guardian",
            correlation_id=policy_event.correlation_id,
            causation_id=policy_event.event_id,
            payload={
                "order_id": "demo_order",
                "proposal_id": policy_event.payload.get("proposal_id"),
                "stake": policy_event.payload.get("approved_stake", 0.0),
                "execution_mode": "demo",
            },
        )
