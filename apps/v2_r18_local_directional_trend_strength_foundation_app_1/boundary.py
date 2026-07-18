from dataclasses import dataclass


@dataclass(frozen=True)
class V2R18DirectionalStrengthBoundary:
    paper_only: bool = True
    local_only: bool = True
    registered_artifact_only: bool = True
    operator_review_required: bool = True
    live_source_allowed: bool = False
    prediction_allowed: bool = False
    trend_label_or_direction_claim_allowed: bool = False
    threshold_or_crossover_allowed: bool = False
    score_rank_or_signal_allowed: bool = False
    network_access_allowed: bool = False
    account_or_execution_allowed: bool = False

    def __post_init__(self) -> None:
        if not all(
            (
                self.paper_only,
                self.local_only,
                self.registered_artifact_only,
                self.operator_review_required,
            )
        ):
            raise ValueError("mandatory directional strength boundary is open")
        if any(
            (
                self.live_source_allowed,
                self.prediction_allowed,
                self.trend_label_or_direction_claim_allowed,
                self.threshold_or_crossover_allowed,
                self.score_rank_or_signal_allowed,
                self.network_access_allowed,
                self.account_or_execution_allowed,
            )
        ):
            raise ValueError("prohibited capability requested")


V2_R18_DIRECTIONAL_STRENGTH_BOUNDARY = V2R18DirectionalStrengthBoundary()
