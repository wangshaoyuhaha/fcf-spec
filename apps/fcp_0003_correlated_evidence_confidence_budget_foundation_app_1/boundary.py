from dataclasses import dataclass


@dataclass(frozen=True)
class CorrelatedEvidenceConfidenceBudgetBoundary:
    paper_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    sidecar_only: bool = True
    registered_artifact_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True
    deterministic_authority_preserved: bool = True
    registered_evidence_authority_preserved: bool = True
    ai_advisory_only: bool = True
    automatic_scoring_allowed: bool = False
    automatic_weight_change_allowed: bool = False
    automatic_approval_allowed: bool = False
    factor_activation_allowed: bool = False
    network_allowed: bool = False
    credential_allowed: bool = False
    execution_allowed: bool = False
    phase_authorization_allowed: bool = False

    def __post_init__(self) -> None:
        required = (
            self.paper_only,
            self.local_only,
            self.loopback_only,
            self.sidecar_only,
            self.registered_artifact_only,
            self.read_only,
            self.operator_review_required,
            self.deterministic_authority_preserved,
            self.registered_evidence_authority_preserved,
            self.ai_advisory_only,
        )
        prohibited = (
            self.automatic_scoring_allowed,
            self.automatic_weight_change_allowed,
            self.automatic_approval_allowed,
            self.factor_activation_allowed,
            self.network_allowed,
            self.credential_allowed,
            self.execution_allowed,
            self.phase_authorization_allowed,
        )
        if not all(required) or any(prohibited):
            raise ValueError("confidence budget boundary must remain fail-closed")


FCP_0003_BOUNDARY = CorrelatedEvidenceConfidenceBudgetBoundary()
