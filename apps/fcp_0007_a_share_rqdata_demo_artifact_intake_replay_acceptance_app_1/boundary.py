from dataclasses import dataclass


@dataclass(frozen=True)
class RQDataDemoAcceptanceBoundary:
    local_file_read_allowed: bool = True
    schema_replay_allowed: bool = True
    source_mutation_allowed: bool = False
    raw_redistribution_allowed: bool = False
    raw_repository_storage_allowed: bool = False
    network_allowed: bool = False
    credential_access_allowed: bool = False
    provider_selection_allowed: bool = False
    commercial_entitlement_claim_allowed: bool = False
    realtime_authorization_allowed: bool = False
    product_phase_authorization_allowed: bool = False
    product_readiness_claim_allowed: bool = False
    execution_allowed: bool = False
    deterministic_authority_preserved: bool = True
    registered_evidence_authority_preserved: bool = True
    ai_advisory_only: bool = True
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        if not self.local_file_read_allowed or not self.schema_replay_allowed:
            raise ValueError("FCP-0007 must permit bounded local schema replay")
        denied = (
            self.source_mutation_allowed,
            self.raw_redistribution_allowed,
            self.raw_repository_storage_allowed,
            self.network_allowed,
            self.credential_access_allowed,
            self.provider_selection_allowed,
            self.commercial_entitlement_claim_allowed,
            self.realtime_authorization_allowed,
            self.product_phase_authorization_allowed,
            self.product_readiness_claim_allowed,
            self.execution_allowed,
        )
        if any(denied):
            raise ValueError("FCP-0007 boundary must fail closed")
        required = (
            self.deterministic_authority_preserved,
            self.registered_evidence_authority_preserved,
            self.ai_advisory_only,
            self.operator_review_required,
        )
        if not all(required):
            raise ValueError("FCP-0007 authority boundary is incomplete")


FCP_0007_BOUNDARY = RQDataDemoAcceptanceBoundary()
