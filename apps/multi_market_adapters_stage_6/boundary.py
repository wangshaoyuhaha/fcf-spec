from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MultiMarketAdapterBoundary:
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
    credential_access_allowed: bool = False
    account_access_allowed: bool = False
    wallet_access_allowed: bool = False
    broker_connection_allowed: bool = False
    exchange_connection_allowed: bool = False
    balance_access_allowed: bool = False
    position_access_allowed: bool = False
    order_path_allowed: bool = False
    real_execution_allowed: bool = False
    live_model_invocation_allowed: bool = False
    prompt_execution_allowed: bool = False
    automatic_activation_allowed: bool = False

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
            self.network_retrieval_allowed,
            self.credential_access_allowed,
            self.account_access_allowed,
            self.wallet_access_allowed,
            self.broker_connection_allowed,
            self.exchange_connection_allowed,
            self.balance_access_allowed,
            self.position_access_allowed,
            self.order_path_allowed,
            self.real_execution_allowed,
            self.live_model_invocation_allowed,
            self.prompt_execution_allowed,
            self.automatic_activation_allowed,
        )
        if not all(required):
            raise ValueError("multi-market authority flags must remain enabled")
        if any(prohibited):
            raise ValueError("prohibited multi-market capability cannot be enabled")


MULTI_MARKET_ADAPTER_BOUNDARY = MultiMarketAdapterBoundary()
