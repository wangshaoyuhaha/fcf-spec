from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class V2R6LocalPaperScenarioBoundary:
    paper_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    sidecar_only: bool = True
    registered_artifact_only: bool = True
    read_only_presentation: bool = True
    operator_review_required: bool = True
    deterministic_engine_authority_preserved: bool = True
    registered_evidence_authority_preserved: bool = True
    network_access_allowed: bool = False
    live_source_allowed: bool = False
    virtual_account_allowed: bool = False
    paper_order_allowed: bool = False
    portfolio_allowed: bool = False
    position_allowed: bool = False
    leverage_allowed: bool = False
    margin_allowed: bool = False
    liquidation_allowed: bool = False
    model_invocation_allowed: bool = False
    prompt_execution_allowed: bool = False
    automatic_learning_allowed: bool = False
    real_execution_allowed: bool = False

    def __post_init__(self) -> None:
        required = (
            self.paper_only,
            self.local_only,
            self.loopback_only,
            self.sidecar_only,
            self.registered_artifact_only,
            self.read_only_presentation,
            self.operator_review_required,
            self.deterministic_engine_authority_preserved,
            self.registered_evidence_authority_preserved,
        )
        prohibited = (
            self.network_access_allowed,
            self.live_source_allowed,
            self.virtual_account_allowed,
            self.paper_order_allowed,
            self.portfolio_allowed,
            self.position_allowed,
            self.leverage_allowed,
            self.margin_allowed,
            self.liquidation_allowed,
            self.model_invocation_allowed,
            self.prompt_execution_allowed,
            self.automatic_learning_allowed,
            self.real_execution_allowed,
        )
        if not all(value is True for value in required):
            raise ValueError("V2-R6 required authority boundary is disabled")
        if any(value is not False for value in prohibited):
            raise ValueError("V2-R6 prohibited capability is enabled")


V2_R6_LOCAL_PAPER_SCENARIO_BOUNDARY = V2R6LocalPaperScenarioBoundary()
