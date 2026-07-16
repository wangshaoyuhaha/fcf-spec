from __future__ import annotations

from dataclasses import dataclass

from .boundary import PORTFOLIO_STAGE_7_BOUNDARY
from .contracts import (
    ConstructionStatus,
    PortfolioOperatorReviewPacket,
    PortfolioStressOutcome,
    StressStatus,
)


@dataclass(frozen=True)
class PortfolioStage7Acceptance:
    status: str
    construction_app_id: str
    stress_app_id: str
    operator_review_required: bool = True
    automatic_activation_allowed: bool = False


def build_stage7_acceptance(
    stress: PortfolioStressOutcome,
    packet: PortfolioOperatorReviewPacket,
) -> PortfolioStage7Acceptance:
    if stress.construction.status is not ConstructionStatus.READY_FOR_STRESS_TEST:
        raise ValueError("portfolio construction is not ready")
    if stress.status is not StressStatus.PASS:
        raise ValueError("portfolio stress suite is not ready")
    payload = packet.payload
    if payload["request_id"] != stress.construction.request.request_id:
        raise ValueError("portfolio review packet linkage failed")
    if (
        payload["operator_review_required"] is not True
        or payload["automatic_approval_allowed"] is not False
        or payload["automatic_rebalance_allowed"] is not False
        or payload["real_execution_allowed"] is not False
        or payload["paper_position_proposal_only"] is not True
    ):
        raise ValueError("portfolio review packet boundary failed")
    if (
        not PORTFOLIO_STAGE_7_BOUNDARY.paper_position_proposal_allowed
        or PORTFOLIO_STAGE_7_BOUNDARY.automatic_rebalance_allowed
        or PORTFOLIO_STAGE_7_BOUNDARY.real_execution_allowed
    ):
        raise ValueError("portfolio Stage 7 boundary failed")
    return PortfolioStage7Acceptance(
        status="PASS",
        construction_app_id="PORTFOLIO-CONSTRUCTION-APP-1",
        stress_app_id="PORTFOLIO-STRESS-TEST-APP-1",
    )
