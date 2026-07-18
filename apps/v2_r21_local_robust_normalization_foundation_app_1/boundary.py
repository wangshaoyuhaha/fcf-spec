from dataclasses import dataclass


@dataclass(frozen=True)
class V2R21NormalizationBoundary:
    paper_only: bool = True
    local_only: bool = True
    registered_artifact_only: bool = True
    operator_review_required: bool = True
    prediction_allowed: bool = False
    factor_direction_allowed: bool = False
    weight_score_rank_or_signal_allowed: bool = False
    network_access_allowed: bool = False
    account_or_execution_allowed: bool = False

    def __post_init__(self) -> None:
        if not all((self.paper_only, self.local_only, self.registered_artifact_only, self.operator_review_required)):
            raise ValueError("mandatory normalization boundary is open")
        if any((self.prediction_allowed, self.factor_direction_allowed, self.weight_score_rank_or_signal_allowed, self.network_access_allowed, self.account_or_execution_allowed)):
            raise ValueError("prohibited capability requested")


V2_R21_NORMALIZATION_BOUNDARY = V2R21NormalizationBoundary()
