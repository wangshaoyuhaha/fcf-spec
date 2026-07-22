from __future__ import annotations

from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import identifier

from .contracts import (
    BTCPerpetualPaperStressScenarioDefinition,
    BTCPerpetualPaperStressScenarioRegistry,
)


def resolve_btc_perpetual_paper_stress_scenario_definition(
    registry: BTCPerpetualPaperStressScenarioRegistry,
    *,
    scenario_id: str,
) -> BTCPerpetualPaperStressScenarioDefinition:
    if not isinstance(registry, BTCPerpetualPaperStressScenarioRegistry):
        raise TypeError("registry must be typed FCP-0056 evidence")
    target = identifier(scenario_id, "scenario_id")
    matches = tuple(
        item for item in registry.definitions if item.scenario_id == target
    )
    if len(matches) != 1:
        raise LookupError("registered stress scenario definition is missing or ambiguous")
    return matches[0]
