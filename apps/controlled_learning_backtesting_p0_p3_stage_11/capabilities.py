from types import MappingProxyType


P0_P3_CAPABILITY_REGISTRY = MappingProxyType(
    {
        "P0": (
            "DATA-SOURCE-VERSION-LOCK-APP-1",
            "POINT-IN-TIME-SNAPSHOT-APP-1",
            "MARKET-CALENDAR-REGISTRY-APP-1",
            "CORPORATE-ACTION-REGISTRY-APP-1",
            "CONFIG-SNAPSHOT-REGISTRY-APP-1",
            "BENCHMARK-REGISTRY-APP-1",
        ),
        "P1": (
            "UNIFIED-MULTI-MARKET-BACKTEST-APP-1",
            "BACKTEST-BIAS-GUARD-APP-1",
            "WALK-FORWARD-VALIDATION-APP-1",
            "BACKTEST-RESULT-REGISTRY-APP-1",
            "OUTCOME-LABEL-REGISTRY-APP-1",
            "FACTOR-AND-PORTFOLIO-ATTRIBUTION-APP-1",
        ),
        "P2": (
            "AI-POINT-IN-TIME-REPLAY-APP-1",
            "AI-KNOWLEDGE-LEAKAGE-GUARD-APP-1",
            "AI-FACT-ALIGNMENT-EVALUATION-APP-1",
            "MODEL-ROLE-PERFORMANCE-APP-1",
            "AI-INCREMENTAL-VALUE-EVALUATION-APP-1",
        ),
        "P3": (
            "HUMAN-FEEDBACK-LEARNING-APP-1",
            "CHAMPION-CHALLENGER-EXPERIMENT-APP-1",
            "CONTROLLED-EVOLUTION-GATE-APP-1",
            "PROMOTION-ROLLBACK-APP-1",
            "LEARNING-LOOP-AUDIT-APP-1",
        ),
    }
)
