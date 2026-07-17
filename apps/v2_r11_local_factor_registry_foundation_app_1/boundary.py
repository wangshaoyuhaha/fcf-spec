from dataclasses import dataclass


@dataclass(frozen=True)
class V2R11FactorRegistryBoundary:
    paper_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    registered_artifact_only: bool = True
    read_only_presentation: bool = True
    operator_review_required: bool = True
    deterministic_engine_authority: bool = True
    registered_evidence_authority: bool = True
    ai_advisory_only: bool = True
    factor_calculation_allowed: bool = False
    factor_activation_allowed: bool = False
    scoring_or_ranking_allowed: bool = False
    network_access_allowed: bool = False
    model_or_prompt_allowed: bool = False
    automatic_learning_allowed: bool = False
    account_or_execution_allowed: bool = False

    def __post_init__(self) -> None:
        required = (
            self.paper_only,
            self.local_only,
            self.loopback_only,
            self.registered_artifact_only,
            self.read_only_presentation,
            self.operator_review_required,
            self.deterministic_engine_authority,
            self.registered_evidence_authority,
            self.ai_advisory_only,
        )
        prohibited = (
            self.factor_calculation_allowed,
            self.factor_activation_allowed,
            self.scoring_or_ranking_allowed,
            self.network_access_allowed,
            self.model_or_prompt_allowed,
            self.automatic_learning_allowed,
            self.account_or_execution_allowed,
        )
        if not all(value is True for value in required):
            raise ValueError("V2-R11 required boundary is disabled")
        if any(value is not False for value in prohibited):
            raise ValueError("V2-R11 prohibited capability is enabled")


V2_R11_LOCAL_FACTOR_REGISTRY_BOUNDARY = V2R11FactorRegistryBoundary()
