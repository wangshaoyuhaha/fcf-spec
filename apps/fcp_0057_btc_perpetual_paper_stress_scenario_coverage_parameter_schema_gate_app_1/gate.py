from __future__ import annotations

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0056_btc_perpetual_paper_stress_scenario_definition_registry_app_1 import (
    BTC_STRESS_SCENARIO_KINDS,
    BTCPerpetualPaperStressScenarioRegistry,
)

from .contracts import (
    BTC_STRESS_PARAMETER_SCHEMA,
    BTCPerpetualPaperStressCoverageSnapshot,
)


def build_btc_perpetual_paper_stress_coverage_snapshot(
    registry: BTCPerpetualPaperStressScenarioRegistry,
    *,
    gate_id: str = "btc-paper-stress-coverage-gate-v1",
) -> BTCPerpetualPaperStressCoverageSnapshot:
    if not isinstance(registry, BTCPerpetualPaperStressScenarioRegistry):
        raise TypeError("registry must be typed FCP-0056 evidence")
    definitions_by_kind: dict[str, list[object]] = {
        kind: [] for kind in BTC_STRESS_SCENARIO_KINDS
    }
    for definition in registry.definitions:
        definitions_by_kind[definition.scenario_kind].append(definition)
    missing = tuple(
        kind for kind, definitions in definitions_by_kind.items() if not definitions
    )
    duplicate = tuple(
        kind for kind, definitions in definitions_by_kind.items() if len(definitions) > 1
    )
    if missing:
        raise ValueError("stress scenario coverage is incomplete")
    if duplicate:
        raise ValueError("stress scenario coverage contains duplicate kinds")
    schema_by_kind = dict(BTC_STRESS_PARAMETER_SCHEMA)
    ordered_definitions = tuple(
        definitions_by_kind[kind][0] for kind in BTC_STRESS_SCENARIO_KINDS
    )
    for definition in ordered_definitions:
        actual = tuple(
            (parameter.parameter_id, parameter.unit_id)
            for parameter in definition.parameters
        )
        if actual != schema_by_kind[definition.scenario_kind]:
            raise ValueError("stress scenario parameter schema mismatch")
    parameter_schema_hash = canonical_sha256(
        {
            "schema": [
                {
                    "parameters": [
                        {"parameter_id": parameter_id, "unit_id": unit_id}
                        for parameter_id, unit_id in parameters
                    ],
                    "scenario_kind": kind,
                }
                for kind, parameters in BTC_STRESS_PARAMETER_SCHEMA
            ],
            "schema_version": "btc-perpetual-paper-stress-parameter-schema-v1",
        }
    )
    return BTCPerpetualPaperStressCoverageSnapshot(
        gate_id=gate_id,
        registry_id=registry.registry_id,
        registry_hash=registry.registry_hash,
        complete_rule_bundle_hash=registry.complete_rule_bundle.snapshot_hash,
        venue_id=registry.complete_rule_bundle.venue_id,
        contract_id=registry.complete_rule_bundle.contract_id,
        registry_as_of_utc=registry.as_of_utc,
        covered_scenario_kinds=BTC_STRESS_SCENARIO_KINDS,
        definition_hashes=tuple(
            definition.definition_hash for definition in ordered_definitions
        ),
        parameter_schema_hash=parameter_schema_hash,
    )
