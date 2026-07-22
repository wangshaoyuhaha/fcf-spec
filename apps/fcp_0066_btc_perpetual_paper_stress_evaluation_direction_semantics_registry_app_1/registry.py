from __future__ import annotations

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0065_btc_perpetual_paper_stress_evaluation_context_coherence_gate_app_1 import (
    BTCPerpetualPaperStressEvaluationContextSnapshot,
)

from .contracts import (
    BTC_STRESS_EVALUATION_DIRECTION_SCHEMA,
    BTCPerpetualPaperStressDirectionSemantics,
    BTCPerpetualPaperStressDirectionSemanticsRegistry,
)


def build_btc_perpetual_paper_stress_direction_semantics_registry(
    evaluation_context: BTCPerpetualPaperStressEvaluationContextSnapshot,
    *,
    as_of_utc: str,
    registry_id: str = "btc-paper-stress-direction-semantics-v1",
) -> BTCPerpetualPaperStressDirectionSemanticsRegistry:
    if not isinstance(
        evaluation_context,
        BTCPerpetualPaperStressEvaluationContextSnapshot,
    ):
        raise TypeError("evaluation_context must be typed FCP-0065 evidence")
    semantics = tuple(
        BTCPerpetualPaperStressDirectionSemantics(
            scenario_kind=kind,
            direction_id=direction_id,
            comparison_family_id=comparison_family_id,
            operand_roles=operand_roles,
            equality_policy_id=equality_policy_id,
        )
        for (
            kind,
            direction_id,
            comparison_family_id,
            operand_roles,
            equality_policy_id,
        ) in BTC_STRESS_EVALUATION_DIRECTION_SCHEMA
    )
    schema_version = "btc-perpetual-paper-stress-direction-semantics-v1"
    direction_schema_hash = canonical_sha256(
        {
            "schema_version": schema_version,
            "semantics": [
                {
                    "comparison_family_id": item.comparison_family_id,
                    "direction_id": item.direction_id,
                    "equality_policy_id": item.equality_policy_id,
                    "operand_roles": list(item.operand_roles),
                    "scenario_kind": item.scenario_kind,
                }
                for item in semantics
            ],
        }
    )
    return BTCPerpetualPaperStressDirectionSemanticsRegistry(
        registry_id=registry_id,
        evaluation_context_snapshot_hash=evaluation_context.snapshot_hash,
        scenario_registry_hash=evaluation_context.scenario_registry_hash,
        extended_readiness_snapshot_hash=(
            evaluation_context.extended_readiness_snapshot_hash
        ),
        operand_evidence_registry_hash=(
            evaluation_context.operand_evidence_registry_hash
        ),
        operand_schema_snapshot_hash=evaluation_context.operand_schema_snapshot_hash,
        complete_rule_bundle_hash=evaluation_context.complete_rule_bundle_hash,
        venue_id=evaluation_context.venue_id,
        contract_id=evaluation_context.contract_id,
        context_as_of_utc=evaluation_context.context_as_of_utc,
        as_of_utc=as_of_utc,
        scenario_kinds=evaluation_context.scenario_kinds,
        semantics=semantics,
        direction_schema_hash=direction_schema_hash,
    )
