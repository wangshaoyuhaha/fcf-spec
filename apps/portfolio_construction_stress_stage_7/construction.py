from __future__ import annotations

from collections import defaultdict
from decimal import Decimal, ROUND_DOWN
from types import MappingProxyType

from apps.multi_market_adapters_stage_6 import AdapterStatus

from .contracts import (
    ConstructionStatus,
    PaperPosition,
    PortfolioConstructionOutcome,
    PortfolioConstructionRequest,
    RankedCandidate,
)


ZERO = Decimal("0")
ONE = Decimal("1")


def _allocate_weights(
    candidates: tuple[RankedCandidate, ...],
    budget: Decimal,
    single_cap: Decimal,
) -> dict[str, Decimal]:
    weights = {item.symbol: ZERO for item in candidates}
    active = list(candidates)
    remaining = budget
    while active and remaining > ZERO:
        score_total = sum((item.deterministic_score for item in active), ZERO)
        if score_total <= ZERO:
            break
        capped: list[RankedCandidate] = []
        for item in active:
            proposed = remaining * item.deterministic_score / score_total
            if proposed > single_cap:
                weights[item.symbol] = single_cap
                remaining -= single_cap
                capped.append(item)
        if not capped:
            for item in active:
                weights[item.symbol] = (
                    remaining * item.deterministic_score / score_total
                )
            remaining = ZERO
            break
        active = [item for item in active if item not in capped]
    return weights


class PortfolioConstructionService:
    def construct(
        self, request: PortfolioConstructionRequest
    ) -> PortfolioConstructionOutcome:
        if not isinstance(request, PortfolioConstructionRequest):
            raise TypeError("request must be a PortfolioConstructionRequest")
        policy = request.policy
        exclusions: list[str] = []
        eligible: list[RankedCandidate] = []
        for item in request.candidates:
            if item.adapter_status is AdapterStatus.BLOCKED:
                exclusions.append(f"excluded-{item.symbol}-adapter-blocked")
            elif item.deterministic_score <= ZERO:
                exclusions.append(f"excluded-{item.symbol}-score-nonpositive")
            elif item.average_daily_value < policy.min_average_daily_value:
                exclusions.append(f"excluded-{item.symbol}-liquidity")
            elif item.max_drawdown < policy.max_drawdown:
                exclusions.append(f"excluded-{item.symbol}-drawdown")
            else:
                eligible.append(item)
        weights = _allocate_weights(
            tuple(eligible), policy.risk_budget_fraction, policy.max_single_weight
        )
        all_weights = {item.symbol: weights.get(item.symbol, ZERO) for item in request.candidates}
        breaches: list[str] = []
        positions: list[PaperPosition] = []
        industry_weights: dict[str, Decimal] = defaultdict(lambda: ZERO)
        theme_weights: dict[str, Decimal] = defaultdict(lambda: ZERO)
        factor_exposures: dict[str, Decimal] = defaultdict(lambda: ZERO)
        portfolio_beta = ZERO
        portfolio_volatility = ZERO
        for item in eligible:
            weight = weights[item.symbol]
            if weight <= ZERO:
                continue
            notional = policy.target_notional * weight
            lot_notional = item.price * item.lot_size
            lots = (notional / lot_notional).to_integral_value(rounding=ROUND_DOWN)
            quantity = int(lots) * item.lot_size
            if quantity <= 0:
                breaches.append(f"paper-quantity-zero-{item.symbol}")
            if notional > item.average_daily_value * policy.max_liquidity_participation:
                breaches.append(f"liquidity-capacity-breach-{item.symbol}")
            industry_weights[item.industry] += weight
            theme_weights[item.theme] += weight
            for factor_id, exposure in item.factor_exposures.items():
                factor_exposures[factor_id] += weight * exposure
            portfolio_beta += weight * item.beta
            portfolio_volatility += weight * item.annualized_volatility
            positions.append(
                PaperPosition(
                    symbol=item.symbol,
                    proposed_weight=weight,
                    proposed_notional=notional,
                    paper_quantity=quantity,
                    price=item.price,
                    asset_class=item.asset_class,
                    industry=item.industry,
                    theme=item.theme,
                    factor_exposures=item.factor_exposures,
                    beta=item.beta,
                    annualized_volatility=item.annualized_volatility,
                    average_daily_value=item.average_daily_value,
                    evidence_ids=item.evidence_ids,
                )
            )
        for name, value in sorted(industry_weights.items()):
            if value > policy.max_industry_weight:
                breaches.append(f"industry-concentration-breach-{name}")
        for name, value in sorted(theme_weights.items()):
            if value > policy.max_theme_weight:
                breaches.append(f"theme-concentration-breach-{name}")
        for name, value in sorted(factor_exposures.items()):
            if abs(value) > policy.max_factor_exposure:
                breaches.append(f"factor-concentration-breach-{name}")
        position_symbols = {item.symbol for item in positions}
        for index, left in enumerate(request.candidates):
            if left.symbol not in position_symbols:
                continue
            for right in request.candidates[index + 1:]:
                if right.symbol not in position_symbols:
                    continue
                values = []
                if right.symbol in left.pair_correlations:
                    values.append(left.pair_correlations[right.symbol])
                if left.symbol in right.pair_correlations:
                    values.append(right.pair_correlations[left.symbol])
                if values and max(values) > policy.max_pair_correlation:
                    breaches.append(
                        f"correlation-breach-{left.symbol}-{right.symbol}"
                    )
        if abs(portfolio_beta) > policy.max_portfolio_beta:
            breaches.append("portfolio-beta-breach")
        if portfolio_volatility > policy.max_portfolio_volatility:
            breaches.append("portfolio-volatility-breach")
        turnover = sum(
            (
                abs(all_weights[item.symbol] - item.current_paper_weight)
                for item in request.candidates
            ),
            ZERO,
        ) / Decimal("2")
        transaction_cost = (
            turnover
            * policy.target_notional
            * policy.transaction_cost_bps
            / Decimal("10000")
        )
        if turnover > policy.max_turnover:
            breaches.append("portfolio-turnover-breach")
        if transaction_cost > policy.max_transaction_cost:
            breaches.append("transaction-cost-breach")
        invested_weight = sum((item.proposed_weight for item in positions), ZERO)
        if invested_weight > policy.risk_budget_fraction:
            breaches.append("risk-budget-breach")
        if not positions:
            breaches.append("no-eligible-paper-position")
        status = (
            ConstructionStatus.BLOCKED
            if breaches
            else ConstructionStatus.READY_FOR_STRESS_TEST
        )
        return PortfolioConstructionOutcome(
            request=request,
            status=status,
            positions=tuple(positions),
            cash_weight=ONE - invested_weight,
            turnover=turnover,
            estimated_transaction_cost=transaction_cost,
            portfolio_beta=portfolio_beta,
            portfolio_volatility=portfolio_volatility,
            reason_codes=tuple(sorted(set(exclusions + breaches))),
        )


def exposure_summary(
    outcome: PortfolioConstructionOutcome,
) -> MappingProxyType[str, object]:
    industries: dict[str, Decimal] = defaultdict(lambda: ZERO)
    themes: dict[str, Decimal] = defaultdict(lambda: ZERO)
    factors: dict[str, Decimal] = defaultdict(lambda: ZERO)
    for item in outcome.positions:
        industries[item.industry] += item.proposed_weight
        themes[item.theme] += item.proposed_weight
        for factor_id, exposure in item.factor_exposures.items():
            factors[factor_id] += item.proposed_weight * exposure
    return MappingProxyType(
        {
            "factor_exposures": MappingProxyType(dict(sorted(factors.items()))),
            "industry_weights": MappingProxyType(dict(sorted(industries.items()))),
            "theme_weights": MappingProxyType(dict(sorted(themes.items()))),
        }
    )
