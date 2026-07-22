from __future__ import annotations

from apps.fcp_0056_btc_perpetual_paper_stress_scenario_definition_registry_app_1 import (
    BTCPerpetualPaperStressScenarioRegistry,
)
from apps.fcp_0070_btc_perpetual_paper_stress_deterministic_trigger_evaluation_app_1 import (
    BTCPerpetualPaperStressDeterministicTriggerEvaluation,
)

from .contracts import (
    BTCPerpetualPaperStressTriggerResultReviewRecord,
    BTCPerpetualPaperStressTriggerResultReviewRegistry,
)


def build_btc_perpetual_paper_stress_trigger_result_review_registry(
    evaluation: BTCPerpetualPaperStressDeterministicTriggerEvaluation,
    scenario_registry: BTCPerpetualPaperStressScenarioRegistry,
    *,
    registered_at_utc: str,
    registry_id: str = "btc-perpetual-paper-stress-trigger-result-review-registry-v1",
) -> BTCPerpetualPaperStressTriggerResultReviewRegistry:
    if not isinstance(
        evaluation,
        BTCPerpetualPaperStressDeterministicTriggerEvaluation,
    ):
        raise TypeError("evaluation must be typed FCP-0070 evidence")
    if not isinstance(scenario_registry, BTCPerpetualPaperStressScenarioRegistry):
        raise TypeError("scenario_registry must be typed FCP-0056 evidence")
    if evaluation.scenario_registry_hash != scenario_registry.registry_hash:
        raise ValueError("scenario registry lineage mismatch")
    if evaluation.complete_rule_bundle_hash != (
        scenario_registry.complete_rule_bundle.snapshot_hash
    ):
        raise ValueError("complete rule bundle lineage mismatch")
    if (evaluation.venue_id, evaluation.contract_id) != (
        scenario_registry.complete_rule_bundle.venue_id,
        scenario_registry.complete_rule_bundle.contract_id,
    ):
        raise ValueError("review venue or contract lineage mismatch")
    definitions = {item.scenario_kind: item for item in scenario_registry.definitions}
    records = []
    for result in evaluation.results:
        definition = definitions[result.scenario_kind]
        records.append(
            BTCPerpetualPaperStressTriggerResultReviewRecord(
                scenario_kind=result.scenario_kind,
                scenario_id=definition.scenario_id,
                version_id=definition.version_id,
                definition_hash=definition.definition_hash,
                severity=definition.severity,
                horizon_seconds=definition.horizon_seconds,
                result_hash=result.result_hash,
                evaluation_snapshot_hash=evaluation.snapshot_hash,
                formula_family_id=result.formula_family_id,
                comparison_operator_id=result.comparison_operator_id,
                measure_value=result.measure_value,
                measure_unit_id=result.measure_unit_id,
                transformed_parameter_value=result.transformed_parameter_value,
                parameter_unit_id=result.parameter_unit_id,
                triggered=result.triggered,
            )
        )
    return BTCPerpetualPaperStressTriggerResultReviewRegistry(
        registry_id=registry_id,
        evaluation_snapshot_hash=evaluation.snapshot_hash,
        scenario_registry_hash=scenario_registry.registry_hash,
        complete_rule_bundle_hash=scenario_registry.complete_rule_bundle.snapshot_hash,
        venue_id=evaluation.venue_id,
        contract_id=evaluation.contract_id,
        evaluated_at_utc=evaluation.evaluated_at_utc,
        scenario_as_of_utc=scenario_registry.as_of_utc,
        registered_at_utc=registered_at_utc,
        records=tuple(records),
    )
