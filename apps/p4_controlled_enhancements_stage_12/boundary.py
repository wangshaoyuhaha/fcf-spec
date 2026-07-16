from dataclasses import dataclass


@dataclass(frozen=True)
class P4ControlledEnhancementsBoundary:
    paper_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    sidecar_only: bool = True
    registered_artifact_only: bool = True
    point_in_time_required: bool = True
    deterministic_authority: bool = True
    ai_advisory_only: bool = True
    operator_review_required: bool = True
    read_only_presentation: bool = True
    network_retrieval_allowed: bool = False
    model_invocation_allowed: bool = False
    prompt_execution_allowed: bool = False
    training_execution_allowed: bool = False
    experiment_execution_allowed: bool = False
    automatic_promotion_allowed: bool = False
    automatic_activation_allowed: bool = False
    automatic_rollback_allowed: bool = False
    archive_mutation_allowed: bool = False
    real_execution_allowed: bool = False

    def __post_init__(self) -> None:
        required = (
            self.paper_only,
            self.local_only,
            self.loopback_only,
            self.sidecar_only,
            self.registered_artifact_only,
            self.point_in_time_required,
            self.deterministic_authority,
            self.ai_advisory_only,
            self.operator_review_required,
            self.read_only_presentation,
        )
        prohibited = (
            self.network_retrieval_allowed,
            self.model_invocation_allowed,
            self.prompt_execution_allowed,
            self.training_execution_allowed,
            self.experiment_execution_allowed,
            self.automatic_promotion_allowed,
            self.automatic_activation_allowed,
            self.automatic_rollback_allowed,
            self.archive_mutation_allowed,
            self.real_execution_allowed,
        )
        if not all(required) or any(prohibited):
            raise ValueError("P4 controlled-enhancement boundary is immutable")


P4_CONTROLLED_ENHANCEMENTS_BOUNDARY = P4ControlledEnhancementsBoundary()
