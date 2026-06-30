from uuid import uuid4

from fcf.contracts.event import create_event
from fcf.core.event_bus import EventBus
from fcf.core.event_store import EventStore


def run_minimal_spine() -> EventStore:
    correlation_id = str(uuid4())

    event_bus = EventBus()
    event_store = EventStore()

    event_bus.subscribe_all(event_store.record)

    raw_event = create_event(
        event_name="fcf.data.raw_received",
        source_module="data_ingestor",
        correlation_id=correlation_id,
        payload={
            "data_type": "demo",
            "source": "manual_demo",
            "data_body": {"message": "hello FCF"},
        },
    )
    event_bus.publish(raw_event)

    normalized_event = create_event(
        event_name="fcf.data.normalized",
        source_module="normalizer",
        correlation_id=correlation_id,
        causation_id=raw_event.event_id,
        payload={
            "data_type": "demo",
            "quality_score": 1.0,
            "normalized_data": {"message": "hello FCF"},
        },
    )
    event_bus.publish(normalized_event)

    regime_event = create_event(
        event_name="fcf.regime.detected",
        source_module="regime_radar",
        correlation_id=correlation_id,
        causation_id=normalized_event.event_id,
        payload={
            "target_id": "demo_target",
            "regime": "demo_ready",
            "confidence": 1.0,
        },
    )
    event_bus.publish(regime_event)

    decision_event = create_event(
        event_name="fcf.decision.proposed",
        source_module="strategy_proposer",
        correlation_id=correlation_id,
        causation_id=regime_event.event_id,
        payload={
            "proposal_id": "demo_proposal",
            "target_id": "demo_target",
            "direction": "observe_only",
            "confidence": 1.0,
            "suggested_stake": 0.0,
        },
    )
    event_bus.publish(decision_event)

    return event_store


if __name__ == "__main__":
    store = run_minimal_spine()

    print("FCF minimal spine executed.")
    print(f"events_recorded: {store.count()}")

    for event in store.all_events():
        print(
            f"{event.sequence_id} | {event.event_name} | "
            f"source={event.source_module}"
        )
