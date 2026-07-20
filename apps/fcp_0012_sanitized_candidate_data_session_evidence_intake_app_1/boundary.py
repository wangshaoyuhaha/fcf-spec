from dataclasses import dataclass


@dataclass(frozen=True)
class SanitizedSessionEvidenceBoundary:
    phase_id: str = "FCF-FCP-0012-SANITIZED-CANDIDATE-DATA-SESSION-EVIDENCE-INTAKE-APP-1"
    paper_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    sidecar_only: bool = True
    registered_artifact_only: bool = True
    read_only_presentation: bool = True
    operator_review_required: bool = True
    deterministic_engine_authority: bool = True
    registered_evidence_authority: bool = True
    ai_advisory_only: bool = True
    external_network_allowed: bool = False
    credentials_allowed: bool = False
    raw_market_values_allowed: bool = False
    provider_selection_allowed: bool = False
    entitlement_approval_allowed: bool = False
    realtime_activation_allowed: bool = False
    trading_or_execution_allowed: bool = False

    def __post_init__(self) -> None:
        required = (
            self.paper_only,
            self.local_only,
            self.loopback_only,
            self.sidecar_only,
            self.registered_artifact_only,
            self.read_only_presentation,
            self.operator_review_required,
            self.deterministic_engine_authority,
            self.registered_evidence_authority,
            self.ai_advisory_only,
        )
        prohibited = (
            self.external_network_allowed,
            self.credentials_allowed,
            self.raw_market_values_allowed,
            self.provider_selection_allowed,
            self.entitlement_approval_allowed,
            self.realtime_activation_allowed,
            self.trading_or_execution_allowed,
        )
        if not all(required) or any(prohibited):
            raise ValueError("FCP-0012 boundary cannot be weakened")


FCP_0012_BOUNDARY = SanitizedSessionEvidenceBoundary()
