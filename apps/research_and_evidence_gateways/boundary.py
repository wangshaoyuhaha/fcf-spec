from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchAndEvidenceBoundary:
    paper_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    sidecar_only: bool = True
    registered_receipt_only: bool = True
    registered_artifact_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True
    deterministic_authority_preserved: bool = True
    registered_evidence_authority_preserved: bool = True
    arbitrary_network_transport_allowed: bool = False
    authenticated_request_allowed: bool = False
    credential_material_allowed: bool = False
    browser_automation_allowed: bool = False
    scraping_allowed: bool = False
    order_path_allowed: bool = False
    real_execution_allowed: bool = False
    automatic_activation_allowed: bool = False

    def __post_init__(self) -> None:
        required = (
            self.paper_only, self.local_only, self.loopback_only,
            self.sidecar_only, self.registered_receipt_only,
            self.registered_artifact_only, self.read_only,
            self.operator_review_required,
            self.deterministic_authority_preserved,
            self.registered_evidence_authority_preserved,
        )
        if not all(required):
            raise ValueError("research gateway authority flags must remain enabled")
        prohibited = (
            self.arbitrary_network_transport_allowed,
            self.authenticated_request_allowed,
            self.credential_material_allowed,
            self.browser_automation_allowed,
            self.scraping_allowed,
            self.order_path_allowed,
            self.real_execution_allowed,
            self.automatic_activation_allowed,
        )
        if any(prohibited):
            raise ValueError("prohibited research gateway capability cannot be enabled")


RESEARCH_AND_EVIDENCE_BOUNDARY = ResearchAndEvidenceBoundary()
