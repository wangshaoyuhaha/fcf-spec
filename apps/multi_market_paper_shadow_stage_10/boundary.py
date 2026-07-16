from dataclasses import dataclass


@dataclass(frozen=True)
class MultiMarketPaperShadowBoundary:
    paper_only: bool = True
    local_only: bool = True
    sidecar_only: bool = True
    registered_artifact_only: bool = True
    historical_forward_separation_required: bool = True
    deterministic_authority: bool = True
    operator_review_required: bool = True
    ai_advisory_only: bool = True
    network_access_allowed: bool = False
    model_invocation_allowed: bool = False
    real_execution_allowed: bool = False
    automatic_approval_allowed: bool = False
    automatic_promotion_allowed: bool = False
    automatic_learning_allowed: bool = False
    automatic_baseline_replacement_allowed: bool = False

    def __post_init__(self) -> None:
        required = (
            self.paper_only,
            self.local_only,
            self.sidecar_only,
            self.registered_artifact_only,
            self.historical_forward_separation_required,
            self.deterministic_authority,
            self.operator_review_required,
            self.ai_advisory_only,
        )
        prohibited = (
            self.network_access_allowed,
            self.model_invocation_allowed,
            self.real_execution_allowed,
            self.automatic_approval_allowed,
            self.automatic_promotion_allowed,
            self.automatic_learning_allowed,
            self.automatic_baseline_replacement_allowed,
        )
        if not all(required) or any(prohibited):
            raise ValueError("Stage 10 validation boundary is immutable")


MULTI_MARKET_PAPER_SHADOW_BOUNDARY = MultiMarketPaperShadowBoundary()
