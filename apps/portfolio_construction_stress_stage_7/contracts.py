from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import Enum
from types import MappingProxyType
from typing import Any

from apps.multi_market_adapters_stage_6 import AdapterStatus, MarketAdapterId


_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/+-]{0,127}$")


def identifier(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if _IDENTIFIER.fullmatch(normalized) is None:
        raise ValueError(f"{field_name} must be a safe identifier")
    return normalized


def decimal_value(value: object, field_name: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be numeric")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name} must be numeric") from exc
    if not result.is_finite():
        raise ValueError(f"{field_name} must be finite")
    return result


def freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {str(key): freeze(item) for key, item in sorted(value.items())}
        )
    if isinstance(value, (list, tuple)):
        return tuple(freeze(item) for item in value)
    if isinstance(value, Decimal):
        return value
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    raise TypeError("portfolio values must be immutable JSON-compatible values")


class ConstructionStatus(str, Enum):
    READY_FOR_STRESS_TEST = "READY_FOR_STRESS_TEST"
    BLOCKED = "BLOCKED"


class StressStatus(str, Enum):
    PASS = "PASS"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class RankedCandidate:
    candidate_id: str
    symbol: str
    market_adapter_id: MarketAdapterId
    adapter_status: AdapterStatus
    rank: int
    deterministic_score: Decimal
    asset_class: str
    industry: str
    theme: str
    factor_exposures: Mapping[str, Decimal]
    pair_correlations: Mapping[str, Decimal]
    beta: Decimal
    annualized_volatility: Decimal
    average_daily_value: Decimal
    max_drawdown: Decimal
    price: Decimal
    lot_size: int
    current_paper_weight: Decimal
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name in ("candidate_id", "symbol", "asset_class", "industry", "theme"):
            object.__setattr__(
                self, field_name, identifier(getattr(self, field_name), field_name)
            )
        object.__setattr__(self, "market_adapter_id", MarketAdapterId(self.market_adapter_id))
        object.__setattr__(self, "adapter_status", AdapterStatus(self.adapter_status))
        if self.rank < 1 or self.lot_size < 1:
            raise ValueError("rank and lot_size must be positive integers")
        for field_name in (
            "deterministic_score", "beta", "annualized_volatility",
            "average_daily_value", "max_drawdown", "price", "current_paper_weight",
        ):
            object.__setattr__(
                self, field_name, decimal_value(getattr(self, field_name), field_name)
            )
        if self.deterministic_score < 0 or self.annualized_volatility < 0:
            raise ValueError("score and volatility must be non-negative")
        if self.average_daily_value < 0 or self.price <= 0:
            raise ValueError("liquidity and price inputs are invalid")
        if not Decimal("-1") <= self.max_drawdown <= Decimal("0"):
            raise ValueError("max_drawdown must be between -1 and 0")
        if not Decimal("0") <= self.current_paper_weight <= Decimal("1"):
            raise ValueError("current_paper_weight must be between 0 and 1")
        factors = {
            identifier(key, "factor_id"): decimal_value(value, "factor_exposure")
            for key, value in self.factor_exposures.items()
        }
        correlations = {
            identifier(key, "correlation_symbol"): decimal_value(value, "correlation")
            for key, value in self.pair_correlations.items()
        }
        if any(value < -1 or value > 1 for value in correlations.values()):
            raise ValueError("pair correlations must be between -1 and 1")
        object.__setattr__(self, "factor_exposures", freeze(factors))
        object.__setattr__(self, "pair_correlations", freeze(correlations))
        evidence_ids = tuple(sorted({identifier(item, "evidence_id") for item in self.evidence_ids}))
        if not evidence_ids:
            raise ValueError("candidate evidence_ids must not be empty")
        object.__setattr__(self, "evidence_ids", evidence_ids)


@dataclass(frozen=True)
class PortfolioPolicy:
    policy_id: str
    version: str
    evidence_ids: tuple[str, ...]
    target_notional: Decimal
    risk_budget_fraction: Decimal
    max_single_weight: Decimal
    max_industry_weight: Decimal
    max_theme_weight: Decimal
    max_factor_exposure: Decimal
    max_pair_correlation: Decimal
    max_portfolio_beta: Decimal
    max_portfolio_volatility: Decimal
    min_average_daily_value: Decimal
    max_drawdown: Decimal
    max_turnover: Decimal
    max_liquidity_participation: Decimal
    transaction_cost_bps: Decimal
    max_transaction_cost: Decimal
    max_stress_loss_fraction: Decimal
    operator_review_required: bool = True
    automatic_activation_allowed: bool = False

    def __post_init__(self) -> None:
        for field_name in ("policy_id", "version"):
            object.__setattr__(self, field_name, identifier(getattr(self, field_name), field_name))
        evidence_ids = tuple(sorted({identifier(item, "evidence_id") for item in self.evidence_ids}))
        if not evidence_ids:
            raise ValueError("policy evidence_ids must not be empty")
        object.__setattr__(self, "evidence_ids", evidence_ids)
        numeric_fields = (
            "target_notional", "risk_budget_fraction", "max_single_weight",
            "max_industry_weight", "max_theme_weight", "max_factor_exposure",
            "max_pair_correlation", "max_portfolio_beta", "max_portfolio_volatility",
            "min_average_daily_value", "max_drawdown", "max_turnover",
            "max_liquidity_participation", "transaction_cost_bps",
            "max_transaction_cost", "max_stress_loss_fraction",
        )
        for field_name in numeric_fields:
            object.__setattr__(self, field_name, decimal_value(getattr(self, field_name), field_name))
        if self.target_notional <= 0:
            raise ValueError("target_notional must be positive")
        fractions = (
            self.risk_budget_fraction, self.max_single_weight,
            self.max_industry_weight, self.max_theme_weight,
            self.max_factor_exposure, self.max_pair_correlation,
            self.max_portfolio_volatility, self.max_turnover,
            self.max_liquidity_participation, self.max_stress_loss_fraction,
        )
        if any(value < 0 or value > 1 for value in fractions):
            raise ValueError("portfolio fraction controls must be between 0 and 1")
        if self.max_drawdown < -1 or self.max_drawdown > 0:
            raise ValueError("max_drawdown policy must be between -1 and 0")
        if self.max_portfolio_beta < 0 or self.min_average_daily_value < 0:
            raise ValueError("portfolio limits must be non-negative")
        if self.transaction_cost_bps < 0 or self.max_transaction_cost < 0:
            raise ValueError("transaction cost controls must be non-negative")
        if self.operator_review_required is not True or self.automatic_activation_allowed is not False:
            raise ValueError("portfolio policy review boundary failed")


@dataclass(frozen=True)
class PortfolioConstructionRequest:
    request_id: str
    correlation_id: str
    ranking_artifact_id: str
    candidates: tuple[RankedCandidate, ...]
    policy: PortfolioPolicy
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        for field_name in ("request_id", "correlation_id", "ranking_artifact_id"):
            object.__setattr__(self, field_name, identifier(getattr(self, field_name), field_name))
        if not self.candidates:
            raise ValueError("portfolio candidates must not be empty")
        ranks = tuple(item.rank for item in self.candidates)
        if ranks != tuple(sorted(ranks)) or len(set(ranks)) != len(ranks):
            raise ValueError("portfolio candidates must preserve unique deterministic rank order")
        if len({item.symbol for item in self.candidates}) != len(self.candidates):
            raise ValueError("portfolio candidate symbols must be unique")
        if self.operator_review_required is not True:
            raise ValueError("operator_review_required must be true")


@dataclass(frozen=True)
class PaperPosition:
    symbol: str
    proposed_weight: Decimal
    proposed_notional: Decimal
    paper_quantity: int
    price: Decimal
    asset_class: str
    industry: str
    theme: str
    factor_exposures: Mapping[str, Decimal]
    beta: Decimal
    annualized_volatility: Decimal
    average_daily_value: Decimal
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class PortfolioConstructionOutcome:
    request: PortfolioConstructionRequest
    status: ConstructionStatus
    positions: tuple[PaperPosition, ...]
    cash_weight: Decimal
    turnover: Decimal
    estimated_transaction_cost: Decimal
    portfolio_beta: Decimal
    portfolio_volatility: Decimal
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class StressScenario:
    scenario_id: str
    version: str
    evidence_ids: tuple[str, ...]
    market_return_shock: Decimal
    volatility_multiplier: Decimal
    liquidity_haircut: Decimal
    asset_class_shocks: Mapping[str, Decimal]
    industry_shocks: Mapping[str, Decimal]
    theme_shocks: Mapping[str, Decimal]
    factor_shocks: Mapping[str, Decimal]

    def __post_init__(self) -> None:
        for field_name in ("scenario_id", "version"):
            object.__setattr__(self, field_name, identifier(getattr(self, field_name), field_name))
        evidence = tuple(sorted({identifier(item, "evidence_id") for item in self.evidence_ids}))
        if not evidence:
            raise ValueError("scenario evidence_ids must not be empty")
        object.__setattr__(self, "evidence_ids", evidence)
        for field_name in ("market_return_shock", "volatility_multiplier", "liquidity_haircut"):
            object.__setattr__(self, field_name, decimal_value(getattr(self, field_name), field_name))
        if self.volatility_multiplier < 0 or not Decimal("0") <= self.liquidity_haircut <= Decimal("1"):
            raise ValueError("stress multipliers are invalid")
        for field_name in ("asset_class_shocks", "industry_shocks", "theme_shocks", "factor_shocks"):
            source = getattr(self, field_name)
            frozen = freeze({identifier(key, field_name): decimal_value(value, field_name) for key, value in source.items()})
            object.__setattr__(self, field_name, frozen)


@dataclass(frozen=True)
class ScenarioResult:
    scenario_id: str
    status: StressStatus
    loss_amount: Decimal
    loss_fraction: Decimal
    stressed_volatility: Decimal
    position_loss_attribution: Mapping[str, Decimal]
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class PortfolioStressOutcome:
    construction: PortfolioConstructionOutcome
    status: StressStatus
    scenario_results: tuple[ScenarioResult, ...]
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class PortfolioOperatorReviewPacket:
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", freeze(self.payload))
