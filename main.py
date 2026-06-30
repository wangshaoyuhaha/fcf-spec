from fcf.core.event_bus import EventBus
from fcf.core.event_store import EventStore
from fcf.data.ingestor import DataIngestor
from fcf.data.normalizer import Normalizer
from fcf.intelligence.regime_radar import RegimeRadar
from fcf.decision.strategy_proposer import StrategyProposer
from fcf.risk.policy_engine import PolicyEngine
from fcf.risk.risk_guardian import RiskGuardian
from fcf.execution.executor import Executor
from fcf.shadow.simulator import ShadowSimulator


def run_minimal_spine() -> EventStore:
    event_bus = EventBus()
    event_store = EventStore()

    event_bus.subscribe_all(event_store.record)

    ingestor = DataIngestor()
    normalizer = Normalizer()
    regime_radar = RegimeRadar()
    strategy_proposer = StrategyProposer()
    policy_engine = PolicyEngine()
    risk_guardian = RiskGuardian()
    executor = Executor()
    shadow_simulator = ShadowSimulator()

    raw_event = ingestor.ingest_demo_data()
    event_bus.publish(raw_event)

    normalized_event = normalizer.normalize(raw_event)
    event_bus.publish(normalized_event)

    regime_event = regime_radar.detect(normalized_event)
    event_bus.publish(regime_event)

    decision_event = strategy_proposer.propose(regime_event)
    event_bus.publish(decision_event)

    policy_event = policy_engine.review(decision_event)
    event_bus.publish(policy_event)

    order_event = risk_guardian.approve(policy_event)
    event_bus.publish(order_event)

    if order_event.event_name == "fcf.order.approved":
        executed_event = executor.execute(order_event)
        event_bus.publish(executed_event)

    shadow_event = shadow_simulator.simulate(decision_event)
    event_bus.publish(shadow_event)

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
