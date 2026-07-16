from __future__ import annotations

from types import MappingProxyType

from .construction import exposure_summary
from .contracts import (
    PortfolioOperatorReviewPacket,
    PortfolioStressOutcome,
)


def _number(value: object) -> str:
    return format(value, "f")


def build_operator_review_packet(
    stress: PortfolioStressOutcome,
) -> PortfolioOperatorReviewPacket:
    construction = stress.construction
    request = construction.request
    exposures = exposure_summary(construction)
    original_candidates = tuple(
        {
            "adapter_status": item.adapter_status.value,
            "asset_class": item.asset_class,
            "average_daily_value": _number(item.average_daily_value),
            "beta": _number(item.beta),
            "candidate_id": item.candidate_id,
            "deterministic_score": _number(item.deterministic_score),
            "evidence_ids": item.evidence_ids,
            "factor_exposures": {
                key: _number(value) for key, value in item.factor_exposures.items()
            },
            "industry": item.industry,
            "market_adapter_id": item.market_adapter_id.value,
            "max_drawdown": _number(item.max_drawdown),
            "rank": item.rank,
            "symbol": item.symbol,
            "theme": item.theme,
            "volatility": _number(item.annualized_volatility),
        }
        for item in request.candidates
    )
    positions = tuple(
        {
            "asset_class": item.asset_class,
            "evidence_ids": item.evidence_ids,
            "industry": item.industry,
            "paper_quantity": item.paper_quantity,
            "price": _number(item.price),
            "proposed_notional": _number(item.proposed_notional),
            "proposed_weight": _number(item.proposed_weight),
            "symbol": item.symbol,
            "theme": item.theme,
        }
        for item in construction.positions
    )
    scenario_results = tuple(
        {
            "loss_amount": _number(item.loss_amount),
            "loss_fraction": _number(item.loss_fraction),
            "position_loss_attribution": {
                key: _number(value)
                for key, value in item.position_loss_attribution.items()
            },
            "reason_codes": item.reason_codes,
            "scenario_id": item.scenario_id,
            "status": item.status.value,
            "stressed_volatility": _number(item.stressed_volatility),
        }
        for item in stress.scenario_results
    )
    return PortfolioOperatorReviewPacket(
        MappingProxyType(
            {
                "automatic_approval_allowed": False,
                "automatic_rebalance_allowed": False,
                "cash_weight": _number(construction.cash_weight),
                "construction_reason_codes": construction.reason_codes,
                "construction_status": construction.status.value,
                "correlation_id": request.correlation_id,
                "estimated_transaction_cost": _number(
                    construction.estimated_transaction_cost
                ),
                "exposures": {
                    group: {key: _number(value) for key, value in values.items()}
                    for group, values in exposures.items()
                },
                "operator_review_required": True,
                "original_ranked_candidates": original_candidates,
                "paper_position_proposal_only": True,
                "policy_id": request.policy.policy_id,
                "policy_version": request.policy.version,
                "portfolio_beta": _number(construction.portfolio_beta),
                "portfolio_volatility": _number(
                    construction.portfolio_volatility
                ),
                "positions": positions,
                "ranking_artifact_id": request.ranking_artifact_id,
                "real_execution_allowed": False,
                "request_id": request.request_id,
                "scenario_results": scenario_results,
                "stress_reason_codes": stress.reason_codes,
                "stress_status": stress.status.value,
                "turnover": _number(construction.turnover),
            }
        )
    )
