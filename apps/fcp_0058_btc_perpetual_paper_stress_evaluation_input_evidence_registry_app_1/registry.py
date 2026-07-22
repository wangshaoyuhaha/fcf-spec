from __future__ import annotations

from apps.fcp_0057_btc_perpetual_paper_stress_scenario_coverage_parameter_schema_gate_app_1 import (
    BTCPerpetualPaperStressCoverageSnapshot,
)

from .contracts import (
    BTCPerpetualPaperStressEvaluationInputObservation,
    BTCPerpetualPaperStressEvaluationInputRegistry,
)


def build_btc_perpetual_paper_stress_evaluation_input_registry(
    coverage_snapshot: BTCPerpetualPaperStressCoverageSnapshot,
    observations: tuple[BTCPerpetualPaperStressEvaluationInputObservation, ...],
    *,
    as_of_utc: str,
    registry_id: str = "btc-paper-stress-evaluation-input-registry-v1",
) -> BTCPerpetualPaperStressEvaluationInputRegistry:
    if not isinstance(
        coverage_snapshot,
        BTCPerpetualPaperStressCoverageSnapshot,
    ):
        raise TypeError("coverage_snapshot must be typed FCP-0057 evidence")
    return BTCPerpetualPaperStressEvaluationInputRegistry(
        registry_id=registry_id,
        coverage_snapshot=coverage_snapshot,
        observations=tuple(observations),
        as_of_utc=as_of_utc,
    )


def resolve_btc_perpetual_paper_stress_evaluation_input(
    registry: BTCPerpetualPaperStressEvaluationInputRegistry,
    *,
    scenario_kind: str,
) -> BTCPerpetualPaperStressEvaluationInputObservation:
    if not isinstance(registry, BTCPerpetualPaperStressEvaluationInputRegistry):
        raise TypeError("registry must be typed FCP-0058 evidence")
    target = str(scenario_kind).strip().upper()
    matches = tuple(
        item for item in registry.observations if item.scenario_kind == target
    )
    if len(matches) != 1:
        raise LookupError("registered stress evaluation input is missing or ambiguous")
    return matches[0]
