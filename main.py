import asyncio
import uuid

from fcf.core.event_bus import EventBus
from fcf.storage.audit_store import AuditStore

from fcf.modules.market import emit_mock_market
from fcf.modules.perception import handle_market_snapshot
from fcf.modules.regime import handle_fact_matrix
from fcf.modules.cognitive_unit import handle_regime_detected
from fcf.modules.governor import handle_cognitive_unit
from fcf.modules.simulation import handle_decision_proposal
from fcf.modules.meta import handle_simulation_completed
from fcf.modules.execution import handle_meta_audit


async def main():
    bus = EventBus()
    audit = AuditStore("fcf_events.db")

    bus.subscribe("*", audit.log_event)

    bus.subscribe("fcf.market.snapshot.emitted", lambda e: handle_market_snapshot(e, bus))
    bus.subscribe("fcf.perception.fact_matrix.ready", lambda e: handle_fact_matrix(e, bus))
    bus.subscribe("fcf.regime.detected", lambda e: handle_regime_detected(e, bus))
    bus.subscribe("fcf.cognitive_unit.completed", lambda e: handle_cognitive_unit(e, bus))
    bus.subscribe("fcf.decision.proposal.created", lambda e: handle_decision_proposal(e, bus))
    bus.subscribe("fcf.simulation.completed", lambda e: handle_simulation_completed(e, bus))
    bus.subscribe("fcf.meta.audit.completed", lambda e: handle_meta_audit(e, bus))

    correlation_id = f"corr_{uuid.uuid4().hex[:16]}"
    await emit_mock_market(bus, correlation_id)

    print("FCF Phase 1 spine completed.")
    print(f"correlation_id = {correlation_id}")
    print("Audit DB written: fcf_events.db")

    audit.close()


if __name__ == "__main__":
    asyncio.run(main())
