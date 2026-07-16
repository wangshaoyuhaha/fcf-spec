"""Controlled learning and deterministic backtesting P0-P3 sidecar."""

from .acceptance import P0P3Acceptance, build_p0_p3_acceptance
from .ai_evaluation import (
    AIHistoricalEvaluation,
    RegisteredAIHistoricalEvaluationService,
    RegisteredAIReplay,
)
from .backtest import DeterministicUnifiedBacktestEngine
from .boundary import (
    CONTROLLED_LEARNING_BACKTESTING_BOUNDARY,
    ControlledLearningBacktestingBoundary,
)
from .capabilities import P0_P3_CAPABILITY_REGISTRY
from .contracts import (
    AIReplayMode,
    BacktestObservation,
    BacktestResult,
    BacktestResultRegistry,
    BacktestStatus,
    ConfigSnapshot,
    DatasetSplit,
    PointInTimeEvidence,
    UnifiedBacktestRequest,
)
from .evolution import (
    EVOLUTION_GATE_CHECKS,
    ChampionChallengerExperiment,
    ControlledEvolutionService,
    EvolutionGateDecision,
    HumanFeedback,
    LearningCandidate,
    QualificationRecord,
)
from .presentation import build_p0_p3_console_sections

__all__ = [
    "AIHistoricalEvaluation",
    "AIReplayMode",
    "BacktestObservation",
    "BacktestResult",
    "BacktestResultRegistry",
    "BacktestStatus",
    "CONTROLLED_LEARNING_BACKTESTING_BOUNDARY",
    "ChampionChallengerExperiment",
    "ConfigSnapshot",
    "ControlledEvolutionService",
    "ControlledLearningBacktestingBoundary",
    "DatasetSplit",
    "DeterministicUnifiedBacktestEngine",
    "EVOLUTION_GATE_CHECKS",
    "EvolutionGateDecision",
    "HumanFeedback",
    "LearningCandidate",
    "P0P3Acceptance",
    "P0_P3_CAPABILITY_REGISTRY",
    "PointInTimeEvidence",
    "QualificationRecord",
    "RegisteredAIHistoricalEvaluationService",
    "RegisteredAIReplay",
    "UnifiedBacktestRequest",
    "build_p0_p3_acceptance",
    "build_p0_p3_console_sections",
]
