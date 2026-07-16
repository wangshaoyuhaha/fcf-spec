from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReadOnlyDataGatewayBoundary:
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
    live_vendor_connection_allowed: bool = False
    credential_access_allowed: bool = False
    account_access_allowed: bool = False
    balance_access_allowed: bool = False
    position_access_allowed: bool = False
    wallet_access_allowed: bool = False
    broker_connection_allowed: bool = False
    exchange_connection_allowed: bool = False
    order_path_allowed: bool = False
    real_execution_allowed: bool = False
    automatic_approval_allowed: bool = False
    automatic_promotion_allowed: bool = False
    automatic_baseline_replacement_allowed: bool = False
    automatic_archive_allowed: bool = False
    automatic_learning_activation_allowed: bool = False

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
            raise ValueError("read-only gateway authority flags must remain enabled")

        prohibited = (
            self.network_retrieval_allowed,
            self.live_vendor_connection_allowed,
            self.credential_access_allowed,
            self.account_access_allowed,
            self.balance_access_allowed,
            self.position_access_allowed,
            self.wallet_access_allowed,
            self.broker_connection_allowed,
            self.exchange_connection_allowed,
            self.order_path_allowed,
            self.real_execution_allowed,
            self.automatic_approval_allowed,
            self.automatic_promotion_allowed,
            self.automatic_baseline_replacement_allowed,
            self.automatic_archive_allowed,
            self.automatic_learning_activation_allowed,
        )
        if any(prohibited):
            raise ValueError("prohibited read-only gateway capability cannot be enabled")


READ_ONLY_DATA_GATEWAY_BOUNDARY = ReadOnlyDataGatewayBoundary()
