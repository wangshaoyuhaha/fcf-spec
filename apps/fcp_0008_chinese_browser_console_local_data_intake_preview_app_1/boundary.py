from dataclasses import dataclass


@dataclass(frozen=True)
class ChineseConsoleLocalIntakeBoundary:
    paper_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    sidecar_only: bool = True
    registered_artifact_only: bool = True
    read_only_presentation: bool = True
    operator_review_required: bool = True
    deterministic_authority_preserved: bool = True
    registered_evidence_authority_preserved: bool = True
    ai_advisory_only: bool = True
    ascii_source_required: bool = True
    get_and_head_only: bool = True
    browser_upload_allowed: bool = False
    source_mutation_allowed: bool = False
    automatic_registration_allowed: bool = False
    provider_selection_allowed: bool = False
    realtime_access_allowed: bool = False
    product_readiness_claim_allowed: bool = False
    external_network_allowed: bool = False
    execution_allowed: bool = False

    def __post_init__(self) -> None:
        required = (
            self.paper_only,
            self.local_only,
            self.loopback_only,
            self.sidecar_only,
            self.registered_artifact_only,
            self.read_only_presentation,
            self.operator_review_required,
            self.deterministic_authority_preserved,
            self.registered_evidence_authority_preserved,
            self.ai_advisory_only,
            self.ascii_source_required,
            self.get_and_head_only,
        )
        prohibited = (
            self.browser_upload_allowed,
            self.source_mutation_allowed,
            self.automatic_registration_allowed,
            self.provider_selection_allowed,
            self.realtime_access_allowed,
            self.product_readiness_claim_allowed,
            self.external_network_allowed,
            self.execution_allowed,
        )
        if not all(required) or any(prohibited):
            raise ValueError("FCP-0008 boundary cannot be weakened")


FCP_0008_BOUNDARY = ChineseConsoleLocalIntakeBoundary()
