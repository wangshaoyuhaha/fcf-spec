from __future__ import annotations

from apps.fcp_0060_btc_perpetual_paper_stress_evaluation_readiness_coherence_gate_app_1 import BTCPerpetualPaperStressEvaluationReadinessSnapshot
from apps.fcp_0061_btc_perpetual_paper_stress_scenario_parameter_domain_semantics_hardening_app_1 import BTCPerpetualPaperStressScenarioParameterDomainSnapshot

from .contracts import BTCPerpetualPaperStressExtendedReadinessSnapshot


def build_btc_perpetual_paper_stress_extended_readiness_snapshot(
    readiness: BTCPerpetualPaperStressEvaluationReadinessSnapshot,
    parameter_domain: BTCPerpetualPaperStressScenarioParameterDomainSnapshot,
    *,
    hardening_id: str = "btc-paper-stress-extended-readiness-hardening-v1",
) -> BTCPerpetualPaperStressExtendedReadinessSnapshot:
    if not isinstance(readiness, BTCPerpetualPaperStressEvaluationReadinessSnapshot):
        raise TypeError("readiness must be typed FCP-0060 evidence")
    if not isinstance(parameter_domain, BTCPerpetualPaperStressScenarioParameterDomainSnapshot):
        raise TypeError("parameter_domain must be typed FCP-0061 evidence")
    if readiness.coverage_snapshot_hash != parameter_domain.coverage_snapshot_hash:
        raise ValueError("extended readiness coverage lineage mismatch")
    if readiness.complete_rule_bundle_hash != parameter_domain.complete_rule_bundle_hash:
        raise ValueError("extended readiness complete-rule lineage mismatch")
    if (readiness.venue_id, readiness.contract_id) != (parameter_domain.venue_id, parameter_domain.contract_id):
        raise ValueError("extended readiness venue or contract lineage mismatch")
    if readiness.scenario_kinds != parameter_domain.validated_scenario_kinds:
        raise ValueError("extended readiness scenario lineage mismatch")
    if readiness.definition_hashes != parameter_domain.validated_definition_hashes:
        raise ValueError("extended readiness definition lineage mismatch")
    if readiness.parameter_schema_hash != parameter_domain.parameter_schema_hash:
        raise ValueError("extended readiness parameter schema lineage mismatch")
    if readiness.coverage_as_of_utc != parameter_domain.as_of_utc:
        raise ValueError("extended readiness parameter-domain time lineage mismatch")
    return BTCPerpetualPaperStressExtendedReadinessSnapshot(
        hardening_id=hardening_id,
        readiness_snapshot_hash=readiness.snapshot_hash,
        parameter_domain_snapshot_hash=parameter_domain.snapshot_hash,
        coverage_snapshot_hash=readiness.coverage_snapshot_hash,
        complete_rule_bundle_hash=readiness.complete_rule_bundle_hash,
        venue_id=readiness.venue_id,
        contract_id=readiness.contract_id,
        coverage_as_of_utc=readiness.coverage_as_of_utc,
        parameter_domain_as_of_utc=parameter_domain.as_of_utc,
        input_as_of_utc=readiness.input_as_of_utc,
        scenario_kinds=readiness.scenario_kinds,
        definition_hashes=readiness.definition_hashes,
        parameter_schema_hash=readiness.parameter_schema_hash,
        parameter_domain_schema_hash=parameter_domain.parameter_domain_schema_hash,
    )
