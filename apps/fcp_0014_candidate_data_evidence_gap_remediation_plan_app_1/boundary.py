from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceGapRemediationBoundary:
    paper_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    registered_artifact_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True
    network_allowed: bool = False
    credentials_allowed: bool = False
    provider_contact_allowed: bool = False
    procurement_allowed: bool = False
    provider_selection_allowed: bool = False
    entitlement_approval_allowed: bool = False
    gap_closure_allowed: bool = False
    realtime_activation_allowed: bool = False
    execution_allowed: bool = False

    def __post_init__(self) -> None:
        required = (
            self.paper_only,
            self.local_only,
            self.loopback_only,
            self.registered_artifact_only,
            self.read_only,
            self.operator_review_required,
        )
        forbidden = (
            self.network_allowed,
            self.credentials_allowed,
            self.provider_contact_allowed,
            self.procurement_allowed,
            self.provider_selection_allowed,
            self.entitlement_approval_allowed,
            self.gap_closure_allowed,
            self.realtime_activation_allowed,
            self.execution_allowed,
        )
        if not all(required) or any(forbidden):
            raise ValueError("evidence gap remediation boundary cannot be weakened")


FCP_0014_BOUNDARY = EvidenceGapRemediationBoundary()
