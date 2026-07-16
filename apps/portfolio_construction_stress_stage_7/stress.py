from __future__ import annotations

from decimal import Decimal
from types import MappingProxyType

from .contracts import (
    ConstructionStatus,
    PortfolioConstructionOutcome,
    PortfolioStressOutcome,
    ScenarioResult,
    StressScenario,
    StressStatus,
)


ZERO = Decimal("0")
ONE = Decimal("1")


class PortfolioStressTestService:
    def evaluate(
        self,
        construction: PortfolioConstructionOutcome,
        scenarios: tuple[StressScenario, ...],
    ) -> PortfolioStressOutcome:
        if not isinstance(construction, PortfolioConstructionOutcome):
            raise TypeError("construction must be a PortfolioConstructionOutcome")
        if not scenarios:
            raise ValueError("stress scenarios must not be empty")
        if len({item.scenario_id for item in scenarios}) != len(scenarios):
            raise ValueError("stress scenario identifiers must be unique")
        suite_reasons: list[str] = []
        results: list[ScenarioResult] = []
        if construction.status is ConstructionStatus.BLOCKED:
            suite_reasons.append("construction-not-ready")
        policy = construction.request.policy
        for scenario in scenarios:
            attribution: dict[str, Decimal] = {}
            reasons: list[str] = []
            total_loss = ZERO
            for position in construction.positions:
                shock = position.beta * scenario.market_return_shock
                shock += scenario.asset_class_shocks.get(position.asset_class, ZERO)
                shock += scenario.industry_shocks.get(position.industry, ZERO)
                shock += scenario.theme_shocks.get(position.theme, ZERO)
                for factor_id, exposure in position.factor_exposures.items():
                    shock += exposure * scenario.factor_shocks.get(factor_id, ZERO)
                if shock < -ONE:
                    shock = -ONE
                loss = -(position.proposed_notional * shock)
                attribution[position.symbol] = loss
                total_loss += loss
                stressed_capacity = (
                    position.average_daily_value
                    * policy.max_liquidity_participation
                    * (ONE - scenario.liquidity_haircut)
                )
                if position.proposed_notional > stressed_capacity:
                    reasons.append(f"stressed-liquidity-breach-{position.symbol}")
            loss_fraction = total_loss / policy.target_notional
            stressed_volatility = (
                construction.portfolio_volatility * scenario.volatility_multiplier
            )
            if loss_fraction > policy.max_stress_loss_fraction:
                reasons.append("stress-loss-budget-breach")
            status = StressStatus.BLOCKED if reasons else StressStatus.PASS
            if status is StressStatus.BLOCKED:
                suite_reasons.append(f"scenario-blocked-{scenario.scenario_id}")
            results.append(
                ScenarioResult(
                    scenario_id=scenario.scenario_id,
                    status=status,
                    loss_amount=total_loss,
                    loss_fraction=loss_fraction,
                    stressed_volatility=stressed_volatility,
                    position_loss_attribution=MappingProxyType(dict(sorted(attribution.items()))),
                    reason_codes=tuple(sorted(set(reasons))),
                )
            )
        status = StressStatus.BLOCKED if suite_reasons else StressStatus.PASS
        return PortfolioStressOutcome(
            construction=construction,
            status=status,
            scenario_results=tuple(results),
            reason_codes=tuple(sorted(set(suite_reasons))),
        )
