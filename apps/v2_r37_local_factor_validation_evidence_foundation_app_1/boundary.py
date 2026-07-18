from dataclasses import dataclass


@dataclass(frozen=True)
class V2R37LocalFactorValidationEvidenceBoundary:
    paper_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    sidecar_only: bool = True
    registered_artifact_only: bool = True
    read_only_presentation: bool = True
    operator_review_required: bool = True
    deterministic_engine_authority_preserved: bool = True
    registered_evidence_authority_preserved: bool = True
    network_access_allowed: bool = False
    automatic_pass_allowed: bool = False
    automatic_promotion_allowed: bool = False
    factor_activation_allowed: bool = False
    score_or_rank_allowed: bool = False
    recommendation_allowed: bool = False
    model_invocation_allowed: bool = False
    automatic_learning_allowed: bool = False
    order_or_execution_allowed: bool = False

    def __post_init__(self) -> None:
        required = (
            self.paper_only,
            self.local_only,
            self.loopback_only,
            self.sidecar_only,
            self.registered_artifact_only,
            self.read_only_presentation,
            self.operator_review_required,
            self.deterministic_engine_authority_preserved,
            self.registered_evidence_authority_preserved,
        )
        prohibited = (
            self.network_access_allowed,
            self.automatic_pass_allowed,
            self.automatic_promotion_allowed,
            self.factor_activation_allowed,
            self.score_or_rank_allowed,
            self.recommendation_allowed,
            self.model_invocation_allowed,
            self.automatic_learning_allowed,
            self.order_or_execution_allowed,
        )
        if not all(required):
            raise ValueError("V2-R37 required authority boundary is disabled")
        if any(prohibited):
            raise ValueError("V2-R37 prohibited capability is enabled")


V2_R37_LOCAL_FACTOR_VALIDATION_EVIDENCE_BOUNDARY = V2R37LocalFactorValidationEvidenceBoundary()
