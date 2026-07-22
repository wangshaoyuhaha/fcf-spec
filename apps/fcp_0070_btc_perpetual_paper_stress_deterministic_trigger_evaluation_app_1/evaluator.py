from __future__ import annotations

from decimal import Decimal

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
from apps.fcp_0069_btc_perpetual_paper_stress_evaluation_input_binding_registry_app_1 import (
    BTCPerpetualPaperStressEvaluationInputBindingRegistry,
)

from .contracts import (
    BTCPerpetualPaperStressDeterministicTriggerEvaluation,
    BTCPerpetualPaperStressDeterministicTriggerResult,
)


_FORMULA_BY_KIND = {item[0]: item[1:] for item in BTC_STRESS_EVALUATION_MEASURE_FORMULA_SCHEMA}


def _measure(
    formula_family_id: str,
    values: tuple[Decimal, ...],
    denominator_policy_id: str,
) -> Decimal:
    if denominator_policy_id == "REJECT_NONPOSITIVE_BASELINE" and values[0] <= 0:
        raise ValueError("registered formula requires a positive baseline")
    if formula_family_id == "POSITIVE_RELATIVE_DECREASE":
        decrease = (values[0] - values[1]) / values[0]
        return max(Decimal("0"), decrease)
    if formula_family_id == "ABSOLUTE_DIFFERENCE":
        return abs(values[1] - values[0])
    if formula_family_id == "DIRECT_OBSERVATION":
        return values[0]
    if formula_family_id == "ABSOLUTE_RELATIVE_DIFFERENCE":
        return abs(values[1] - values[0]) / values[0]
    if formula_family_id == "CURRENT_BASELINE_RETENTION_RATIO":
        return values[1] / values[0]
    raise ValueError("formula family is not registered")


def _transform(transform_id: str, value: Decimal) -> Decimal:
    if transform_id == "IDENTITY_PARAMETER":
        return value
    if transform_id == "ABSOLUTE_PARAMETER_MAGNITUDE":
        return abs(value)
    raise ValueError("parameter transform is not registered")


def _compare(operator_id: str, measure: Decimal, parameter: Decimal) -> bool:
    if operator_id == "MEASURE_GREATER_THAN_PARAMETER":
        return measure > parameter
    if operator_id == "MEASURE_LESS_THAN_OR_EQUAL_PARAMETER":
        return measure <= parameter
    if operator_id == "MEASURE_GREATER_THAN_OR_EQUAL_PARAMETER":
        return measure >= parameter
    if operator_id == "MEASURE_LESS_THAN_PARAMETER":
        return measure < parameter
    raise ValueError("comparison operator is not registered")


def evaluate_btc_perpetual_paper_stress_triggers(
    input_bindings: BTCPerpetualPaperStressEvaluationInputBindingRegistry,
    predicate_registry: BTCPerpetualPaperStressTriggerPredicateSemanticsRegistry,
    operand_evidence: BTCPerpetualPaperStressEvaluationOperandEvidenceRegistry,
    scenario_registry: BTCPerpetualPaperStressScenarioRegistry,
    *,
    evaluated_at_utc: str,
    evaluation_id: str = "btc-perpetual-paper-stress-trigger-evaluation-v1",
) -> BTCPerpetualPaperStressDeterministicTriggerEvaluation:
    if not isinstance(input_bindings, BTCPerpetualPaperStressEvaluationInputBindingRegistry):
        raise TypeError("input_bindings must be typed FCP-0069 evidence")
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
    if input_bindings.predicate_registry_hash != predicate_registry.registry_hash:
        raise ValueError("predicate registry lineage mismatch")
    if input_bindings.predicate_schema_hash != predicate_registry.predicate_schema_hash:
        raise ValueError("predicate schema lineage mismatch")
    if input_bindings.operand_evidence_registry_hash != operand_evidence.registry_hash:
        raise ValueError("operand evidence registry lineage mismatch")
    if input_bindings.operand_schema_snapshot_hash != (
        operand_evidence.operand_schema_snapshot.snapshot_hash
    ):
        raise ValueError("operand schema snapshot lineage mismatch")
    if input_bindings.scenario_registry_hash != scenario_registry.registry_hash:
        raise ValueError("scenario registry lineage mismatch")
    if input_bindings.complete_rule_bundle_hash != (
        scenario_registry.complete_rule_bundle.snapshot_hash
    ):
        raise ValueError("complete rule bundle lineage mismatch")
    if predicate_registry.operand_evidence_registry_hash != operand_evidence.registry_hash:
        raise ValueError("predicate operand evidence lineage mismatch")
    if predicate_registry.scenario_registry_hash != scenario_registry.registry_hash:
        raise ValueError("predicate scenario registry lineage mismatch")
    venue_contract = {
        (input_bindings.venue_id, input_bindings.contract_id),
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
        raise ValueError("evaluation venue or contract lineage mismatch")
    predicates = {item.scenario_kind: item for item in predicate_registry.semantics}
    observations = {
        item.observation_hash: item for item in operand_evidence.observations
    }
    definitions = {item.scenario_kind: item for item in scenario_registry.definitions}
    results = []
    for binding in input_bindings.bindings:
        kind = binding.scenario_kind
        predicate = predicates[kind]
        if binding.predicate_semantics_hash != predicate.semantics_hash:
            raise ValueError("bound predicate semantics mismatch")
        try:
            bound_observations = tuple(
                observations[value] for value in binding.observation_hashes
            )
        except KeyError as exc:
            raise ValueError("bound operand observation is not registered") from exc
        if binding.operand_roles != tuple(item.role_id for item in bound_observations):
            raise ValueError("bound operand role order mismatch")
        if any(item.scenario_kind != kind for item in bound_observations):
            raise ValueError("bound operand scenario mismatch")
        (
            formula_family_id,
            operand_roles,
            parameter_id,
            parameter_unit_id,
            output_unit_id,
            parameter_transform_id,
            denominator_policy_id,
        ) = _FORMULA_BY_KIND[kind]
        if binding.operand_roles != operand_roles:
            raise ValueError("bound operands do not match the closed formula")
        parameters = tuple(
            item
            for item in definitions[kind].parameters
            if item.parameter_id == parameter_id
        )
        if len(parameters) != 1:
            raise ValueError("registered scenario parameter is missing or ambiguous")
        parameter = parameters[0]
        if (
            binding.parameter_id != parameter_id
            or binding.parameter_hash != parameter.parameter_hash
            or parameter.unit_id != parameter_unit_id
        ):
            raise ValueError("bound scenario parameter mismatch")
        if predicate.parameter_transform_id != parameter_transform_id:
            raise ValueError("predicate parameter transform mismatch")
        measure = _measure(
            formula_family_id,
            tuple(item.value for item in bound_observations),
            denominator_policy_id,
        )
        transformed_parameter = _transform(parameter_transform_id, parameter.value)
        results.append(
            BTCPerpetualPaperStressDeterministicTriggerResult(
                scenario_kind=kind,
                formula_family_id=formula_family_id,
                comparison_operator_id=predicate.comparison_operator_id,
                measure_value=measure,
                measure_unit_id=output_unit_id,
                transformed_parameter_value=transformed_parameter,
                parameter_unit_id=parameter_unit_id,
                triggered=_compare(
                    predicate.comparison_operator_id,
                    measure,
                    transformed_parameter,
                ),
                input_binding_hash=binding.binding_hash,
                predicate_semantics_hash=predicate.semantics_hash,
            )
        )
    venue_id, contract_id = venue_contract.pop()
    return BTCPerpetualPaperStressDeterministicTriggerEvaluation(
        evaluation_id=evaluation_id,
        input_binding_registry_hash=input_bindings.registry_hash,
        predicate_registry_hash=predicate_registry.registry_hash,
        operand_evidence_registry_hash=operand_evidence.registry_hash,
        scenario_registry_hash=scenario_registry.registry_hash,
        complete_rule_bundle_hash=scenario_registry.complete_rule_bundle.snapshot_hash,
        venue_id=venue_id,
        contract_id=contract_id,
        inputs_as_of_utc=input_bindings.as_of_utc,
        evaluated_at_utc=evaluated_at_utc,
        results=tuple(results),
    )
