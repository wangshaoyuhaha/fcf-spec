from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DataEntitlementProvenanceBoundary:
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
    network_retrieval_allowed: bool = False
    credential_material_allowed: bool = False
    live_vendor_connection_allowed: bool = False
    market_or_vendor_selection_allowed: bool = False
    license_approval_allowed: bool = False
    phase_authorization_allowed: bool = False
    gap_closure_allowed: bool = False
    automatic_activation_allowed: bool = False
    broker_connection_allowed: bool = False
    exchange_connection_allowed: bool = False
    account_access_allowed: bool = False
    balance_access_allowed: bool = False
    position_access_allowed: bool = False
    wallet_access_allowed: bool = False
    order_path_allowed: bool = False
    real_execution_allowed: bool = False

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
        if not all(required):
            raise ValueError("entitlement readiness authority flags must remain enabled")

        prohibited = (
            self.network_retrieval_allowed,
            self.credential_material_allowed,
            self.live_vendor_connection_allowed,
            self.market_or_vendor_selection_allowed,
            self.license_approval_allowed,
            self.phase_authorization_allowed,
            self.gap_closure_allowed,
            self.automatic_activation_allowed,
            self.broker_connection_allowed,
            self.exchange_connection_allowed,
            self.account_access_allowed,
            self.balance_access_allowed,
            self.position_access_allowed,
            self.wallet_access_allowed,
            self.order_path_allowed,
            self.real_execution_allowed,
        )
        if any(prohibited):
            raise ValueError("prohibited entitlement readiness capability cannot be enabled")


FCP_0001_DATA_ENTITLEMENT_PROVENANCE_BOUNDARY = (
    DataEntitlementProvenanceBoundary()
)
