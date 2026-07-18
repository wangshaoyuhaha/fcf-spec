from dataclasses import dataclass


@dataclass(frozen=True)
class V2R39BrowserOperatorFactorGovernanceProjectionBoundary:
    paper_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    sidecar_only: bool = True
    registered_artifact_only: bool = True
    read_only_presentation: bool = True
    operator_review_required: bool = True
    deterministic_engine_authority_preserved: bool = True
    registered_evidence_authority_preserved: bool = True
    network_fetch_allowed: bool = False
    write_controls_allowed: bool = False
    automatic_approval_allowed: bool = False
    automatic_promotion_allowed: bool = False
    factor_activation_allowed: bool = False
    model_invocation_allowed: bool = False
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
            self.network_fetch_allowed,
            self.write_controls_allowed,
            self.automatic_approval_allowed,
            self.automatic_promotion_allowed,
            self.factor_activation_allowed,
            self.model_invocation_allowed,
            self.order_or_execution_allowed,
        )
        if not all(required):
            raise ValueError("V2-R39 required authority boundary is disabled")
        if any(prohibited):
            raise ValueError("V2-R39 prohibited capability is enabled")


V2_R39_BROWSER_OPERATOR_FACTOR_GOVERNANCE_PROJECTION_BOUNDARY = (
    V2R39BrowserOperatorFactorGovernanceProjectionBoundary()
)
