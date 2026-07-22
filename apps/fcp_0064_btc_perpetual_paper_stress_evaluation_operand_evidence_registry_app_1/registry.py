from __future__ import annotations

from apps.fcp_0063_btc_perpetual_paper_stress_evaluation_operand_schema_registry_app_1 import (
    BTCPerpetualPaperStressEvaluationOperandSchemaSnapshot,
)

from .contracts import (
    BTCPerpetualPaperStressEvaluationOperandEvidenceObservation,
    BTCPerpetualPaperStressEvaluationOperandEvidenceRegistry,
)


def build_btc_perpetual_paper_stress_evaluation_operand_evidence_registry(
    operand_schema_snapshot: BTCPerpetualPaperStressEvaluationOperandSchemaSnapshot,
    observations: tuple[
        BTCPerpetualPaperStressEvaluationOperandEvidenceObservation, ...
    ],
    *,
    as_of_utc: str,
    registry_id: str = "btc-paper-stress-evaluation-operand-evidence-registry-v1",
) -> BTCPerpetualPaperStressEvaluationOperandEvidenceRegistry:
    if not isinstance(
        operand_schema_snapshot,
        BTCPerpetualPaperStressEvaluationOperandSchemaSnapshot,
    ):
        raise TypeError("operand_schema_snapshot must be typed FCP-0063 evidence")
    return BTCPerpetualPaperStressEvaluationOperandEvidenceRegistry(
        registry_id=registry_id,
        operand_schema_snapshot=operand_schema_snapshot,
        observations=tuple(observations),
        as_of_utc=as_of_utc,
    )


def resolve_btc_perpetual_paper_stress_evaluation_operand_evidence(
    registry: BTCPerpetualPaperStressEvaluationOperandEvidenceRegistry,
    *,
    scenario_kind: str,
    role_id: str,
) -> BTCPerpetualPaperStressEvaluationOperandEvidenceObservation:
    if not isinstance(
        registry,
        BTCPerpetualPaperStressEvaluationOperandEvidenceRegistry,
    ):
        raise TypeError("registry must be typed FCP-0064 evidence")
    kind = str(scenario_kind).strip().upper()
    role = str(role_id).strip()
    matches = tuple(
        item
        for item in registry.observations
        if item.scenario_kind == kind and item.role_id == role
    )
    if len(matches) != 1:
        raise LookupError("registered stress operand evidence is missing or ambiguous")
    return matches[0]
