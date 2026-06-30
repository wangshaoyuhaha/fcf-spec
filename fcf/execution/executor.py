from fcf.contracts.event import FCFEvent, create_event


class Executor:
    def execute(self, order_event: FCFEvent) -> FCFEvent:
        return create_event(
            event_name="fcf.order.executed",
            source_module="executor",
            correlation_id=order_event.correlation_id,
            causation_id=order_event.event_id,
            payload={
                "order_id": order_event.payload.get("order_id"),
                "executed_price": 1.0,
                "executed_stake": order_event.payload.get("stake", 0.0),
                "slippage": 0.0,
                "status": "filled",
            },
        )
