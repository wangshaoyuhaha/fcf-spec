from dataclasses import dataclass


@dataclass(frozen=True)
class V2R34LocalPolicyWindowLanguageEvidenceBoundary:
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
    semantic_direction_allowed: bool = False
    industry_benefit_allowed: bool = False
    policy_causation_allowed: bool = False
    automatic_taxonomy_mapping_allowed: bool = False
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
            self.semantic_direction_allowed,
            self.industry_benefit_allowed,
            self.policy_causation_allowed,
            self.automatic_taxonomy_mapping_allowed,
            self.factor_activation_allowed,
            self.factor_or_score_allowed,
            self.signal_or_recommendation_allowed,
            self.model_invocation_allowed,
            self.automatic_learning_allowed,
            self.order_or_execution_allowed,
        )
        if not all(required):
            raise ValueError("V2-R34 required authority boundary is disabled")
        if any(prohibited):
            raise ValueError("V2-R34 prohibited capability is enabled")


V2_R34_LOCAL_POLICY_WINDOW_LANGUAGE_EVIDENCE_BOUNDARY = (
    V2R34LocalPolicyWindowLanguageEvidenceBoundary()
)
