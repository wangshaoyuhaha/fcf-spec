from __future__ import annotations

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0056_btc_perpetual_paper_stress_scenario_definition_registry_app_1 import (
    BTCPerpetualPaperStressScenarioRegistry,
)
from apps.fcp_0064_btc_perpetual_paper_stress_evaluation_operand_evidence_registry_app_1 import (
    BTCPerpetualPaperStressEvaluationOperandEvidenceRegistry,
)
from apps.fcp_0067_btc_perpetual_paper_stress_evaluation_measure_formula_semantics_registry_app_1 import (
    BTC_STRESS_EVALUATION_MEASURE_FORMULA_SCHEMA,
)
from apps.fcp_0068_btc_perpetual_paper_stress_evaluation_trigger_predicate_semantics_registry_app_1 import (
    BTCPerpetualPaperStressTriggerPredicateSemanticsRegistry,
)

from .contracts import (
    BTCPerpetualPaperStressEvaluationInputBinding,
    BTCPerpetualPaperStressEvaluationInputBindingRegistry,
)


_PARAMETER_BY_KIND = {
    kind: parameter_id
    for (
        kind,
        _formula,
        _roles,
        parameter_id,
        _parameter_unit,
        _output_unit,
        _transform,
        _denominator,
    ) in BTC_STRESS_EVALUATION_MEASURE_FORMULA_SCHEMA
}


def build_btc_perpetual_paper_stress_evaluation_input_binding_registry(
    predicate_registry: BTCPerpetualPaperStressTriggerPredicateSemanticsRegistry,
    operand_evidence: BTCPerpetualPaperStressEvaluationOperandEvidenceRegistry,
    scenario_registry: BTCPerpetualPaperStressScenarioRegistry,
    *,
    as_of_utc: str,
    registry_id: str = "btc-perpetual-paper-stress-evaluation-input-binding-v1",
) -> BTCPerpetualPaperStressEvaluationInputBindingRegistry:
    if not isinstance(
        predicate_registry,
        BTCPerpetualPaperStressTriggerPredicateSemanticsRegistry,
    ):
        raise TypeError("predicate_registry must be typed FCP-0068 evidence")
    if not isinstance(
        operand_evidence,
        BTCPerpetualPaperStressEvaluationOperandEvidenceRegistry,
    ):
        raise TypeError("operand_evidence must be typed FCP-0064 evidence")
    if not isinstance(scenario_registry, BTCPerpetualPaperStressScenarioRegistry):
        raise TypeError("scenario_registry must be typed FCP-0056 evidence")
    if predicate_registry.operand_evidence_registry_hash != operand_evidence.registry_hash:
        raise ValueError("operand evidence registry lineage mismatch")
    if predicate_registry.operand_schema_snapshot_hash != (
        operand_evidence.operand_schema_snapshot.snapshot_hash
    ):
        raise ValueError("operand schema snapshot lineage mismatch")
    if predicate_registry.scenario_registry_hash != scenario_registry.registry_hash:
        raise ValueError("scenario registry lineage mismatch")
    if predicate_registry.complete_rule_bundle_hash != (
        scenario_registry.complete_rule_bundle.snapshot_hash
    ):
        raise ValueError("complete rule bundle lineage mismatch")
    venue_contract = {
        (predicate_registry.venue_id, predicate_registry.contract_id),
        (
            operand_evidence.operand_schema_snapshot.venue_id,
            operand_evidence.operand_schema_snapshot.contract_id,
        ),
        (
            scenario_registry.complete_rule_bundle.venue_id,
            scenario_registry.complete_rule_bundle.contract_id,
        ),
    }
    if len(venue_contract) != 1:
        raise ValueError("input binding venue or contract lineage mismatch")
    predicates = {item.scenario_kind: item for item in predicate_registry.semantics}
    definitions = {item.scenario_kind: item for item in scenario_registry.definitions}
    observations = {
        kind: tuple(
            item
            for item in operand_evidence.observations
            if item.scenario_kind == kind
        )
        for kind in predicate_registry.scenario_kinds
    }
    bindings = []
    for kind in predicate_registry.scenario_kinds:
        parameter_id = _PARAMETER_BY_KIND[kind]
        parameters = tuple(
            item
            for item in definitions[kind].parameters
            if item.parameter_id == parameter_id
        )
        if len(parameters) != 1:
            raise ValueError("registered scenario parameter is missing or ambiguous")
        kind_observations = observations[kind]
        bindings.append(
            BTCPerpetualPaperStressEvaluationInputBinding(
                scenario_kind=kind,
                predicate_semantics_hash=predicates[kind].semantics_hash,
                operand_roles=tuple(item.role_id for item in kind_observations),
                observation_hashes=tuple(
                    item.observation_hash for item in kind_observations
                ),
                parameter_id=parameter_id,
                parameter_hash=parameters[0].parameter_hash,
            )
        )
    schema_version = "btc-perpetual-paper-stress-evaluation-input-binding-v1"
    binding_schema_hash = canonical_sha256(
        {
            "bindings": [
                {
                    "observation_hashes": list(item.observation_hashes),
                    "operand_roles": list(item.operand_roles),
                    "parameter_hash": item.parameter_hash,
                    "parameter_id": item.parameter_id,
                    "predicate_semantics_hash": item.predicate_semantics_hash,
                    "scenario_kind": item.scenario_kind,
                }
                for item in bindings
            ],
            "schema_version": schema_version,
        }
    )
    venue_id, contract_id = venue_contract.pop()
    return BTCPerpetualPaperStressEvaluationInputBindingRegistry(
        registry_id=registry_id,
        predicate_registry_hash=predicate_registry.registry_hash,
        predicate_schema_hash=predicate_registry.predicate_schema_hash,
        operand_evidence_registry_hash=operand_evidence.registry_hash,
        operand_schema_snapshot_hash=(
            operand_evidence.operand_schema_snapshot.snapshot_hash
        ),
        scenario_registry_hash=scenario_registry.registry_hash,
        complete_rule_bundle_hash=scenario_registry.complete_rule_bundle.snapshot_hash,
        venue_id=venue_id,
        contract_id=contract_id,
        predicate_as_of_utc=predicate_registry.as_of_utc,
        operand_evidence_as_of_utc=operand_evidence.as_of_utc,
        scenario_as_of_utc=scenario_registry.as_of_utc,
        as_of_utc=as_of_utc,
        bindings=tuple(bindings),
        binding_schema_hash=binding_schema_hash,
    )
