from __future__ import annotations

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0062_btc_perpetual_paper_stress_evaluation_readiness_parameter_domain_coherence_hardening_app_1 import (
    BTCPerpetualPaperStressExtendedReadinessSnapshot,
)

from .contracts import (
    BTC_STRESS_EVALUATION_OPERAND_SCHEMA,
    BTCPerpetualPaperStressEvaluationOperandRequirement,
    BTCPerpetualPaperStressEvaluationOperandSchemaSnapshot,
)


def build_btc_perpetual_paper_stress_evaluation_operand_schema_snapshot(
    extended_readiness: BTCPerpetualPaperStressExtendedReadinessSnapshot,
    *,
    registry_id: str = "btc-paper-stress-evaluation-operand-schema-v1",
) -> BTCPerpetualPaperStressEvaluationOperandSchemaSnapshot:
    if not isinstance(
        extended_readiness,
        BTCPerpetualPaperStressExtendedReadinessSnapshot,
    ):
        raise TypeError("extended_readiness must be typed FCP-0062 evidence")
    requirements = tuple(
        BTCPerpetualPaperStressEvaluationOperandRequirement(
            scenario_kind=kind,
            mode_id=mode,
            role_id=role_id,
            metric_id=metric_id,
            unit_id=unit_id,
        )
        for kind, mode, operands in BTC_STRESS_EVALUATION_OPERAND_SCHEMA
        for role_id, metric_id, unit_id in operands
    )
    schema_version = "btc-perpetual-paper-stress-evaluation-operand-schema-v1"
    operand_schema_hash = canonical_sha256(
        {
            "requirements": [
                {
                    "metric_id": item.metric_id,
                    "mode_id": item.mode_id,
                    "role_id": item.role_id,
                    "scenario_kind": item.scenario_kind,
                    "unit_id": item.unit_id,
                }
                for item in requirements
            ],
            "schema_version": schema_version,
        }
    )
    return BTCPerpetualPaperStressEvaluationOperandSchemaSnapshot(
        registry_id=registry_id,
        extended_readiness_snapshot_hash=extended_readiness.snapshot_hash,
        readiness_snapshot_hash=extended_readiness.readiness_snapshot_hash,
        parameter_domain_snapshot_hash=(
            extended_readiness.parameter_domain_snapshot_hash
        ),
        coverage_snapshot_hash=extended_readiness.coverage_snapshot_hash,
        complete_rule_bundle_hash=extended_readiness.complete_rule_bundle_hash,
        venue_id=extended_readiness.venue_id,
        contract_id=extended_readiness.contract_id,
        as_of_utc=extended_readiness.input_as_of_utc,
        scenario_kinds=extended_readiness.scenario_kinds,
        requirements=requirements,
        operand_schema_hash=operand_schema_hash,
    )
