from __future__ import annotations

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0066_btc_perpetual_paper_stress_evaluation_direction_semantics_registry_app_1 import (
    BTCPerpetualPaperStressDirectionSemanticsRegistry,
)

from .contracts import (
    BTC_STRESS_EVALUATION_MEASURE_FORMULA_SCHEMA,
    BTCPerpetualPaperStressMeasureFormulaSemantics,
    BTCPerpetualPaperStressMeasureFormulaSemanticsRegistry,
)


def build_btc_perpetual_paper_stress_measure_formula_semantics_registry(
    direction_registry: BTCPerpetualPaperStressDirectionSemanticsRegistry,
    *,
    as_of_utc: str,
    registry_id: str = "btc-perpetual-paper-stress-measure-formula-semantics-registry-v1",
) -> BTCPerpetualPaperStressMeasureFormulaSemanticsRegistry:
    if not isinstance(
        direction_registry,
        BTCPerpetualPaperStressDirectionSemanticsRegistry,
    ):
        raise TypeError("direction_registry must be typed FCP-0066 evidence")
    semantics = tuple(
        BTCPerpetualPaperStressMeasureFormulaSemantics(
            scenario_kind=kind,
            formula_family_id=formula_family_id,
            operand_roles=operand_roles,
            parameter_id=parameter_id,
            parameter_unit_id=parameter_unit_id,
            output_unit_id=output_unit_id,
            parameter_transform_id=parameter_transform_id,
            denominator_policy_id=denominator_policy_id,
        )
        for (
            kind,
            formula_family_id,
            operand_roles,
            parameter_id,
            parameter_unit_id,
            output_unit_id,
            parameter_transform_id,
            denominator_policy_id,
        ) in BTC_STRESS_EVALUATION_MEASURE_FORMULA_SCHEMA
    )
    schema_version = "btc-perpetual-paper-stress-measure-formula-semantics-v1"
    formula_schema_hash = canonical_sha256(
        {
            "schema_version": schema_version,
            "semantics": [
                {
                    "denominator_policy_id": item.denominator_policy_id,
                    "formula_family_id": item.formula_family_id,
                    "operand_roles": list(item.operand_roles),
                    "output_unit_id": item.output_unit_id,
                    "parameter_id": item.parameter_id,
                    "parameter_transform_id": item.parameter_transform_id,
                    "parameter_unit_id": item.parameter_unit_id,
                    "scenario_kind": item.scenario_kind,
                }
                for item in semantics
            ],
        }
    )
    return BTCPerpetualPaperStressMeasureFormulaSemanticsRegistry(
        registry_id=registry_id,
        direction_registry_hash=direction_registry.registry_hash,
        direction_schema_hash=direction_registry.direction_schema_hash,
        evaluation_context_snapshot_hash=(
            direction_registry.evaluation_context_snapshot_hash
        ),
        scenario_registry_hash=direction_registry.scenario_registry_hash,
        extended_readiness_snapshot_hash=(
            direction_registry.extended_readiness_snapshot_hash
        ),
        operand_evidence_registry_hash=(
            direction_registry.operand_evidence_registry_hash
        ),
        operand_schema_snapshot_hash=(
            direction_registry.operand_schema_snapshot_hash
        ),
        complete_rule_bundle_hash=direction_registry.complete_rule_bundle_hash,
        venue_id=direction_registry.venue_id,
        contract_id=direction_registry.contract_id,
        direction_as_of_utc=direction_registry.as_of_utc,
        as_of_utc=as_of_utc,
        scenario_kinds=direction_registry.scenario_kinds,
        semantics=semantics,
        formula_schema_hash=formula_schema_hash,
    )
