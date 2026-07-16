from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PortfolioStage7Boundary:
    paper_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    sidecar_only: bool = True
    registered_artifact_only: bool = True
    operator_review_required: bool = True
    deterministic_authority_preserved: bool = True
    registered_evidence_authority_preserved: bool = True
    ai_advisory_only: bool = True
    paper_position_proposal_allowed: bool = True
    live_data_retrieval_allowed: bool = False
    credential_access_allowed: bool = False
    account_access_allowed: bool = False
    balance_access_allowed: bool = False
    position_read_allowed: bool = False
    wallet_access_allowed: bool = False
    broker_connection_allowed: bool = False
    exchange_connection_allowed: bool = False
    automatic_rebalance_allowed: bool = False
    order_path_allowed: bool = False
    real_execution_allowed: bool = False
    live_model_invocation_allowed: bool = False
    prompt_execution_allowed: bool = False
    automatic_approval_allowed: bool = False

    def __post_init__(self) -> None:
        required = (
            self.paper_only,
            self.local_only,
            self.loopback_only,
            self.sidecar_only,
            self.registered_artifact_only,
            self.operator_review_required,
            self.deterministic_authority_preserved,
            self.registered_evidence_authority_preserved,
            self.ai_advisory_only,
            self.paper_position_proposal_allowed,
        )
        prohibited = (
            self.live_data_retrieval_allowed,
            self.credential_access_allowed,
            self.account_access_allowed,
            self.balance_access_allowed,
            self.position_read_allowed,
            self.wallet_access_allowed,
            self.broker_connection_allowed,
            self.exchange_connection_allowed,
            self.automatic_rebalance_allowed,
            self.order_path_allowed,
            self.real_execution_allowed,
            self.live_model_invocation_allowed,
            self.prompt_execution_allowed,
            self.automatic_approval_allowed,
        )
        if not all(required):
            raise ValueError("portfolio Stage 7 authority flags must remain enabled")
        if any(prohibited):
            raise ValueError("prohibited portfolio Stage 7 capability cannot be enabled")


PORTFOLIO_STAGE_7_BOUNDARY = PortfolioStage7Boundary()
