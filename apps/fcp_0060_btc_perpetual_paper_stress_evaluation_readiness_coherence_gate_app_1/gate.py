from __future__ import annotations

from apps.fcp_0055_btc_perpetual_complete_rule_bundle_coherence_hardening_app_1 import (
    BTCPerpetualCompleteRuleBundleSnapshot,
)
from apps.fcp_0057_btc_perpetual_paper_stress_scenario_coverage_parameter_schema_gate_app_1 import (
    BTCPerpetualPaperStressCoverageSnapshot,
)
from apps.fcp_0059_btc_perpetual_paper_stress_evaluation_input_domain_semantics_hardening_app_1 import (
    BTCPerpetualPaperStressEvaluationInputDomainSnapshot,
)

from .contracts import BTCPerpetualPaperStressEvaluationReadinessSnapshot


def build_btc_perpetual_paper_stress_evaluation_readiness_snapshot(
    complete_rule_bundle: BTCPerpetualCompleteRuleBundleSnapshot,
    coverage_snapshot: BTCPerpetualPaperStressCoverageSnapshot,
    input_domain_snapshot: BTCPerpetualPaperStressEvaluationInputDomainSnapshot,
    *,
    gate_id: str = "btc-paper-stress-evaluation-readiness-gate-v1",
) -> BTCPerpetualPaperStressEvaluationReadinessSnapshot:
    if not isinstance(complete_rule_bundle, BTCPerpetualCompleteRuleBundleSnapshot):
        raise TypeError("complete_rule_bundle must be typed FCP-0055 evidence")
    if not isinstance(coverage_snapshot, BTCPerpetualPaperStressCoverageSnapshot):
        raise TypeError("coverage_snapshot must be typed FCP-0057 evidence")
    if not isinstance(
        input_domain_snapshot,
        BTCPerpetualPaperStressEvaluationInputDomainSnapshot,
    ):
        raise TypeError("input_domain_snapshot must be typed FCP-0059 evidence")
    if coverage_snapshot.complete_rule_bundle_hash != complete_rule_bundle.snapshot_hash:
        raise ValueError("readiness complete-rule snapshot lineage mismatch")
    if input_domain_snapshot.coverage_snapshot_hash != coverage_snapshot.snapshot_hash:
        raise ValueError("readiness coverage snapshot lineage mismatch")
    identities = {
        (complete_rule_bundle.venue_id, complete_rule_bundle.contract_id),
        (coverage_snapshot.venue_id, coverage_snapshot.contract_id),
        (input_domain_snapshot.venue_id, input_domain_snapshot.contract_id),
    }
    if len(identities) != 1:
        raise ValueError("readiness venue or contract lineage mismatch")
    if (
        input_domain_snapshot.validated_scenario_kinds
        != coverage_snapshot.covered_scenario_kinds
    ):
        raise ValueError("readiness scenario lineage mismatch")
    return BTCPerpetualPaperStressEvaluationReadinessSnapshot(
        gate_id=gate_id,
        complete_rule_bundle_hash=complete_rule_bundle.snapshot_hash,
        coverage_snapshot_hash=coverage_snapshot.snapshot_hash,
        input_domain_snapshot_hash=input_domain_snapshot.snapshot_hash,
        input_registry_hash=input_domain_snapshot.input_registry_hash,
        venue_id=complete_rule_bundle.venue_id,
        contract_id=complete_rule_bundle.contract_id,
        rule_effective_at_utc=complete_rule_bundle.effective_at_utc,
        coverage_as_of_utc=coverage_snapshot.registry_as_of_utc,
        input_as_of_utc=input_domain_snapshot.as_of_utc,
        scenario_kinds=coverage_snapshot.covered_scenario_kinds,
        definition_hashes=coverage_snapshot.definition_hashes,
        observation_hashes=input_domain_snapshot.validated_observation_hashes,
        parameter_schema_hash=coverage_snapshot.parameter_schema_hash,
        domain_schema_hash=input_domain_snapshot.domain_schema_hash,
    )
