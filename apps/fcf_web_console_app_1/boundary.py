from dataclasses import dataclass


@dataclass(frozen=True)
class FCFWebConsoleBoundary:
    paper_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    sidecar_only: bool = True
    registered_artifact_authority_only: bool = True
    operator_review_required: bool = True
    deterministic_engine_authority: bool = True
    registered_evidence_authority: bool = True
    ai_advisory_only: bool = True
    read_only_authoritative_inputs: bool = True
    network_retrieval_allowed: bool = False
    model_invocation_allowed: bool = False
    automatic_transition_allowed: bool = False
    financial_execution_allowed: bool = False

    def __post_init__(self) -> None:
        required = (
            self.paper_only,
            self.local_only,
            self.loopback_only,
            self.sidecar_only,
            self.registered_artifact_authority_only,
            self.operator_review_required,
            self.deterministic_engine_authority,
            self.registered_evidence_authority,
            self.ai_advisory_only,
            self.read_only_authoritative_inputs,
        )
        prohibited = (
            self.network_retrieval_allowed,
            self.model_invocation_allowed,
            self.automatic_transition_allowed,
            self.financial_execution_allowed,
        )
        if not all(required) or any(prohibited):
            raise ValueError("FCF Web Console authority boundary is immutable")


FCF_WEB_CONSOLE_BOUNDARY = FCFWebConsoleBoundary()
