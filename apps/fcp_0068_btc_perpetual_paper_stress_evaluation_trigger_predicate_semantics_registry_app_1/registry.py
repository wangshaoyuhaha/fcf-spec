from __future__ import annotations

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0067_btc_perpetual_paper_stress_evaluation_measure_formula_semantics_registry_app_1 import (
    BTCPerpetualPaperStressMeasureFormulaSemanticsRegistry,
)

from .contracts import (
    BTC_STRESS_EVALUATION_TRIGGER_PREDICATE_SCHEMA,
    BTCPerpetualPaperStressTriggerPredicateSemantics,
    BTCPerpetualPaperStressTriggerPredicateSemanticsRegistry,
)


def build_btc_perpetual_paper_stress_trigger_predicate_semantics_registry(
    formula_registry: BTCPerpetualPaperStressMeasureFormulaSemanticsRegistry,
    *,
    as_of_utc: str,
    registry_id: str = (
        "btc-perpetual-paper-stress-trigger-predicate-semantics-registry-v1"
    ),
) -> BTCPerpetualPaperStressTriggerPredicateSemanticsRegistry:
    if not isinstance(
        formula_registry,
        BTCPerpetualPaperStressMeasureFormulaSemanticsRegistry,
    ):
        raise TypeError("formula_registry must be typed FCP-0067 evidence")
    semantics = tuple(
        BTCPerpetualPaperStressTriggerPredicateSemantics(
            scenario_kind=kind,
            comparison_operator_id=comparison_operator_id,
            left_role_id=left_role_id,
            right_role_id=right_role_id,
            parameter_transform_id=parameter_transform_id,
            boundary_policy_id=boundary_policy_id,
        )
        for (
            kind,
            comparison_operator_id,
            left_role_id,
            right_role_id,
            parameter_transform_id,
            boundary_policy_id,
        ) in BTC_STRESS_EVALUATION_TRIGGER_PREDICATE_SCHEMA
    )
    schema_version = "btc-perpetual-paper-stress-trigger-predicate-semantics-v1"
    predicate_schema_hash = canonical_sha256(
        {
            "schema_version": schema_version,
            "semantics": [
                {
                    "boundary_policy_id": item.boundary_policy_id,
                    "comparison_operator_id": item.comparison_operator_id,
                    "left_role_id": item.left_role_id,
                    "parameter_transform_id": item.parameter_transform_id,
                    "right_role_id": item.right_role_id,
                    "scenario_kind": item.scenario_kind,
                }
                for item in semantics
            ],
        }
    )
    return BTCPerpetualPaperStressTriggerPredicateSemanticsRegistry(
        registry_id=registry_id,
        formula_registry_hash=formula_registry.registry_hash,
        formula_schema_hash=formula_registry.formula_schema_hash,
        direction_registry_hash=formula_registry.direction_registry_hash,
        direction_schema_hash=formula_registry.direction_schema_hash,
        evaluation_context_snapshot_hash=(
            formula_registry.evaluation_context_snapshot_hash
        ),
        scenario_registry_hash=formula_registry.scenario_registry_hash,
        extended_readiness_snapshot_hash=(
            formula_registry.extended_readiness_snapshot_hash
        ),
        operand_evidence_registry_hash=(
            formula_registry.operand_evidence_registry_hash
        ),
        operand_schema_snapshot_hash=formula_registry.operand_schema_snapshot_hash,
        complete_rule_bundle_hash=formula_registry.complete_rule_bundle_hash,
        venue_id=formula_registry.venue_id,
        contract_id=formula_registry.contract_id,
        formula_as_of_utc=formula_registry.as_of_utc,
        as_of_utc=as_of_utc,
        scenario_kinds=formula_registry.scenario_kinds,
        semantics=semantics,
        predicate_schema_hash=predicate_schema_hash,
    )
