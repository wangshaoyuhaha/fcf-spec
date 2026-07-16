from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DataAndCredentialGovernanceBoundary:
    paper_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    sidecar_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True
    deterministic_authority_preserved: bool = True
    registered_evidence_authority_preserved: bool = True
    ai_advisory_only: bool = True
    credential_reference_metadata_allowed: bool = True
    credential_material_allowed: bool = False
    secret_value_allowed: bool = False
    environment_secret_read_allowed: bool = False
    file_secret_read_allowed: bool = False
    network_retrieval_allowed: bool = False
    authenticated_request_allowed: bool = False
    live_vendor_connection_allowed: bool = False
    account_access_allowed: bool = False
    balance_access_allowed: bool = False
    position_access_allowed: bool = False
    wallet_access_allowed: bool = False
    broker_connection_allowed: bool = False
    exchange_connection_allowed: bool = False
    order_path_allowed: bool = False
    real_execution_allowed: bool = False
    automatic_activation_allowed: bool = False

    def __post_init__(self) -> None:
        required = (
            self.paper_only,
            self.local_only,
            self.loopback_only,
            self.sidecar_only,
            self.read_only,
            self.operator_review_required,
            self.deterministic_authority_preserved,
            self.registered_evidence_authority_preserved,
            self.ai_advisory_only,
            self.credential_reference_metadata_allowed,
        )
        if not all(required):
            raise ValueError("governance authority flags must remain enabled")

        prohibited = (
            self.credential_material_allowed,
            self.secret_value_allowed,
            self.environment_secret_read_allowed,
            self.file_secret_read_allowed,
            self.network_retrieval_allowed,
            self.authenticated_request_allowed,
            self.live_vendor_connection_allowed,
            self.account_access_allowed,
            self.balance_access_allowed,
            self.position_access_allowed,
            self.wallet_access_allowed,
            self.broker_connection_allowed,
            self.exchange_connection_allowed,
            self.order_path_allowed,
            self.real_execution_allowed,
            self.automatic_activation_allowed,
        )
        if any(prohibited):
            raise ValueError("prohibited governance capability cannot be enabled")


DATA_AND_CREDENTIAL_GOVERNANCE_BOUNDARY = DataAndCredentialGovernanceBoundary()
