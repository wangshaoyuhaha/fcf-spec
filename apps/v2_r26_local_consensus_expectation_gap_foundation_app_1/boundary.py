from dataclasses import dataclass


@dataclass(frozen=True)
class V2R26LocalConsensusExpectationGapBoundary:
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
    live_source_allowed: bool = False
    ai_generated_consensus_allowed: bool = False
    consensus_imputation_allowed: bool = False
    future_revision_allowed: bool = False
    factor_activation_allowed: bool = False
    factor_or_score_allowed: bool = False
    signal_or_recommendation_allowed: bool = False
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
            self.live_source_allowed,
            self.ai_generated_consensus_allowed,
            self.consensus_imputation_allowed,
            self.future_revision_allowed,
            self.factor_activation_allowed,
            self.factor_or_score_allowed,
            self.signal_or_recommendation_allowed,
            self.model_invocation_allowed,
            self.automatic_learning_allowed,
            self.order_or_execution_allowed,
        )
        if not all(value is True for value in required):
            raise ValueError("V2-R26 required authority boundary is disabled")
        if any(value is not False for value in prohibited):
            raise ValueError("V2-R26 prohibited capability is enabled")


V2_R26_LOCAL_CONSENSUS_EXPECTATION_GAP_BOUNDARY = (
    V2R26LocalConsensusExpectationGapBoundary()
)
