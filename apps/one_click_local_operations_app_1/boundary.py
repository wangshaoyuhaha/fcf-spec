from dataclasses import dataclass


@dataclass(frozen=True)
class OneClickLocalOperationsBoundary:
    paper_only: bool = True
    local_only: bool = True
    exact_loopback_only: bool = True
    sidecar_only: bool = True
    registered_artifact_only: bool = True
    operator_review_required: bool = True
    deterministic_authority_preserved: bool = True
    registered_evidence_authority_preserved: bool = True
    ai_advisory_only: bool = True
    explicit_operator_invocation_required: bool = True
    graceful_stop_required: bool = True
    automatic_baseline_overwrite_allowed: bool = False
    unrelated_process_termination_allowed: bool = False
    public_binding_allowed: bool = False
    financial_execution_allowed: bool = False

    def __post_init__(self) -> None:
        required = (
            self.paper_only,
            self.local_only,
            self.exact_loopback_only,
            self.sidecar_only,
            self.registered_artifact_only,
            self.operator_review_required,
            self.deterministic_authority_preserved,
            self.registered_evidence_authority_preserved,
            self.ai_advisory_only,
            self.explicit_operator_invocation_required,
            self.graceful_stop_required,
        )
        prohibited = (
            self.automatic_baseline_overwrite_allowed,
            self.unrelated_process_termination_allowed,
            self.public_binding_allowed,
            self.financial_execution_allowed,
        )
        if not all(required) or any(prohibited):
            raise ValueError("one-click local operations boundary is immutable")


ONE_CLICK_LOCAL_OPERATIONS_BOUNDARY = OneClickLocalOperationsBoundary()
