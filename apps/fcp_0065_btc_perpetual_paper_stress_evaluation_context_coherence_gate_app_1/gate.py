from __future__ import annotations

from apps.fcp_0056_btc_perpetual_paper_stress_scenario_definition_registry_app_1 import (
    BTCPerpetualPaperStressScenarioRegistry,
)
from apps.fcp_0062_btc_perpetual_paper_stress_evaluation_readiness_parameter_domain_coherence_hardening_app_1 import (
    BTCPerpetualPaperStressExtendedReadinessSnapshot,
)
from apps.fcp_0064_btc_perpetual_paper_stress_evaluation_operand_evidence_registry_app_1 import (
    BTCPerpetualPaperStressEvaluationOperandEvidenceRegistry,
)

from .contracts import BTCPerpetualPaperStressEvaluationContextSnapshot


def build_btc_perpetual_paper_stress_evaluation_context_snapshot(
    scenario_registry: BTCPerpetualPaperStressScenarioRegistry,
    extended_readiness: BTCPerpetualPaperStressExtendedReadinessSnapshot,
    operand_evidence: BTCPerpetualPaperStressEvaluationOperandEvidenceRegistry,
    *,
    as_of_utc: str,
    gate_id: str = "btc-paper-stress-evaluation-context-v1",
) -> BTCPerpetualPaperStressEvaluationContextSnapshot:
    if not isinstance(scenario_registry, BTCPerpetualPaperStressScenarioRegistry):
        raise TypeError("scenario_registry must be typed FCP-0056 evidence")
    if not isinstance(
        extended_readiness,
        BTCPerpetualPaperStressExtendedReadinessSnapshot,
    ):
        raise TypeError("extended_readiness must be typed FCP-0062 evidence")
    if not isinstance(
        operand_evidence,
        BTCPerpetualPaperStressEvaluationOperandEvidenceRegistry,
    ):
        raise TypeError("operand_evidence must be typed FCP-0064 evidence")
    definitions = scenario_registry.definitions
    if tuple(item.scenario_kind for item in definitions) != extended_readiness.scenario_kinds:
        raise ValueError("scenario kind lineage mismatch")
    if tuple(item.definition_hash for item in definitions) != extended_readiness.definition_hashes:
        raise ValueError("scenario definition lineage mismatch")
    if scenario_registry.complete_rule_bundle.snapshot_hash != extended_readiness.complete_rule_bundle_hash:
        raise ValueError("complete rule bundle lineage mismatch")
    schema = operand_evidence.operand_schema_snapshot
    if schema.extended_readiness_snapshot_hash != extended_readiness.snapshot_hash:
        raise ValueError("extended readiness ancestry mismatch")
    if schema.coverage_snapshot_hash != extended_readiness.coverage_snapshot_hash:
        raise ValueError("coverage snapshot lineage mismatch")
    if schema.parameter_domain_snapshot_hash != extended_readiness.parameter_domain_snapshot_hash:
        raise ValueError("parameter domain lineage mismatch")
    if schema.complete_rule_bundle_hash != extended_readiness.complete_rule_bundle_hash:
        raise ValueError("operand schema rule bundle lineage mismatch")
    venue_contract = {
        (scenario_registry.complete_rule_bundle.venue_id, scenario_registry.complete_rule_bundle.contract_id),
        (extended_readiness.venue_id, extended_readiness.contract_id),
        (schema.venue_id, schema.contract_id),
        (operand_evidence.observations[0].venue_id, operand_evidence.observations[0].contract_id),
    }
    if len(venue_contract) != 1:
        raise ValueError("evaluation context venue or contract lineage mismatch")
    return BTCPerpetualPaperStressEvaluationContextSnapshot(
        gate_id=gate_id,
        scenario_registry_id=scenario_registry.registry_id,
        scenario_registry_hash=scenario_registry.registry_hash,
        extended_readiness_snapshot_hash=extended_readiness.snapshot_hash,
        operand_evidence_registry_hash=operand_evidence.registry_hash,
        operand_schema_snapshot_hash=schema.snapshot_hash,
        complete_rule_bundle_hash=extended_readiness.complete_rule_bundle_hash,
        coverage_snapshot_hash=extended_readiness.coverage_snapshot_hash,
        parameter_domain_snapshot_hash=extended_readiness.parameter_domain_snapshot_hash,
        venue_id=extended_readiness.venue_id,
        contract_id=extended_readiness.contract_id,
        scenario_registry_as_of_utc=scenario_registry.as_of_utc,
        extended_readiness_as_of_utc=extended_readiness.input_as_of_utc,
        operand_evidence_as_of_utc=operand_evidence.as_of_utc,
        context_as_of_utc=as_of_utc,
        scenario_kinds=extended_readiness.scenario_kinds,
        scenario_ids=tuple(item.scenario_id for item in definitions),
        version_ids=tuple(item.version_id for item in definitions),
        definition_hashes=tuple(item.definition_hash for item in definitions),
        parameter_hash_groups=tuple(
            tuple(parameter.parameter_hash for parameter in item.parameters)
            for item in definitions
        ),
        operand_observation_hashes=tuple(
            item.observation_hash for item in operand_evidence.observations
        ),
    )
