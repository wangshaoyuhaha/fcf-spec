from dataclasses import dataclass


@dataclass(frozen=True)
class ControlledLearningBacktestingBoundary:
    paper_only: bool = True
    local_only: bool = True
    sidecar_only: bool = True
    registered_artifact_only: bool = True
    point_in_time_required: bool = True
    deterministic_backtest_authority: bool = True
    learning_candidate_only: bool = True
    operator_review_required: bool = True
    model_invocation_allowed: bool = False
    prompt_execution_allowed: bool = False
    result_rewrite_allowed: bool = False
    automatic_promotion_allowed: bool = False
    automatic_activation_allowed: bool = False
    automatic_rollback_allowed: bool = False
    real_execution_allowed: bool = False

    def __post_init__(self) -> None:
        required = (
            self.paper_only,
            self.local_only,
            self.sidecar_only,
            self.registered_artifact_only,
            self.point_in_time_required,
            self.deterministic_backtest_authority,
            self.learning_candidate_only,
            self.operator_review_required,
        )
        prohibited = (
            self.model_invocation_allowed,
            self.prompt_execution_allowed,
            self.result_rewrite_allowed,
            self.automatic_promotion_allowed,
            self.automatic_activation_allowed,
            self.automatic_rollback_allowed,
            self.real_execution_allowed,
        )
        if not all(required) or any(prohibited):
            raise ValueError("P0-P3 authority boundary is immutable")


CONTROLLED_LEARNING_BACKTESTING_BOUNDARY = ControlledLearningBacktestingBoundary()
