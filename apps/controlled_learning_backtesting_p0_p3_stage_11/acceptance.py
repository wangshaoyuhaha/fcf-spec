from dataclasses import dataclass

from .boundary import CONTROLLED_LEARNING_BACKTESTING_BOUNDARY
from .capabilities import P0_P3_CAPABILITY_REGISTRY
from .ai_evaluation import RegisteredAIHistoricalEvaluationService, RegisteredAIReplay
from .backtest import (
    BacktestBiasGuard,
    DeterministicUnifiedBacktestEngine,
    WalkForwardValidator,
)
from .contracts import ConfigSnapshot, PointInTimeEvidence, BacktestResultRegistry
from .evolution import ControlledEvolutionService, HumanFeedback, LearningCandidate
from .registries import (
    AppendOnlyRegistry,
    AttributionRegistry,
    AttributionRecord,
    BenchmarkRecord,
    BenchmarkRegistry,
    CorporateActionRecord,
    CorporateActionRegistry,
    ConfigSnapshotRegistry,
    DataSourceVersionLock,
    DataSourceVersionRegistry,
    MarketCalendarRecord,
    MarketCalendarRegistry,
    OutcomeLabelRecord,
    OutcomeLabelRegistry,
)


P0_P3_IMPLEMENTATION_BINDINGS = {
    "DATA-SOURCE-VERSION-LOCK-APP-1": DataSourceVersionRegistry,
    "POINT-IN-TIME-SNAPSHOT-APP-1": PointInTimeEvidence,
    "MARKET-CALENDAR-REGISTRY-APP-1": MarketCalendarRegistry,
    "CORPORATE-ACTION-REGISTRY-APP-1": CorporateActionRegistry,
    "CONFIG-SNAPSHOT-REGISTRY-APP-1": ConfigSnapshotRegistry,
    "BENCHMARK-REGISTRY-APP-1": BenchmarkRegistry,
    "UNIFIED-MULTI-MARKET-BACKTEST-APP-1": DeterministicUnifiedBacktestEngine,
    "BACKTEST-BIAS-GUARD-APP-1": BacktestBiasGuard,
    "WALK-FORWARD-VALIDATION-APP-1": WalkForwardValidator,
    "BACKTEST-RESULT-REGISTRY-APP-1": BacktestResultRegistry,
    "OUTCOME-LABEL-REGISTRY-APP-1": OutcomeLabelRegistry,
    "FACTOR-AND-PORTFOLIO-ATTRIBUTION-APP-1": AttributionRegistry,
    "AI-POINT-IN-TIME-REPLAY-APP-1": RegisteredAIReplay,
    "AI-KNOWLEDGE-LEAKAGE-GUARD-APP-1": RegisteredAIHistoricalEvaluationService.evaluate,
    "AI-FACT-ALIGNMENT-EVALUATION-APP-1": RegisteredAIHistoricalEvaluationService,
    "MODEL-ROLE-PERFORMANCE-APP-1": RegisteredAIHistoricalEvaluationService,
    "AI-INCREMENTAL-VALUE-EVALUATION-APP-1": RegisteredAIHistoricalEvaluationService,
    "HUMAN-FEEDBACK-LEARNING-APP-1": HumanFeedback,
    "CHAMPION-CHALLENGER-EXPERIMENT-APP-1": ControlledEvolutionService.experiment,
    "CONTROLLED-EVOLUTION-GATE-APP-1": ControlledEvolutionService.gate,
    "PROMOTION-ROLLBACK-APP-1": ControlledEvolutionService.gate,
    "LEARNING-LOOP-AUDIT-APP-1": LearningCandidate,
}


@dataclass(frozen=True)
class P0P3Acceptance:
    status: str
    capability_count: int
    phase_counts: tuple[tuple[str, int], ...]
    next_phase: str

    def __post_init__(self) -> None:
        if self.status != "D1_D6_ACCEPTED" or self.capability_count != 22:
            raise ValueError("P0-P3 capability acceptance is incomplete")
        if self.next_phase != "P4_GOVERNANCE_DECISION":
            raise ValueError("P0-P3 next phase mismatch")


def build_p0_p3_acceptance() -> P0P3Acceptance:
    CONTROLLED_LEARNING_BACKTESTING_BOUNDARY.__post_init__()
    capabilities = {
        item
        for values in P0_P3_CAPABILITY_REGISTRY.values()
        for item in values
    }
    if set(P0_P3_IMPLEMENTATION_BINDINGS) != capabilities:
        raise ValueError("P0-P3 implementation bindings are incomplete")
    if any(not callable(value) for value in P0_P3_IMPLEMENTATION_BINDINGS.values()):
        raise ValueError("P0-P3 implementation binding is not callable")
    return P0P3Acceptance(
        status="D1_D6_ACCEPTED",
        capability_count=sum(
            len(values) for values in P0_P3_CAPABILITY_REGISTRY.values()
        ),
        phase_counts=tuple(
            (phase, len(values))
            for phase, values in P0_P3_CAPABILITY_REGISTRY.items()
        ),
        next_phase="P4_GOVERNANCE_DECISION",
    )
