from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

from apps.multi_market_adapters_stage_6 import AdapterStatus, MarketAdapterId
from apps.portfolio_construction_stress_stage_7 import (
    ConstructionStatus,
    PORTFOLIO_STAGE_7_BOUNDARY,
    PortfolioConstructionRequest,
    PortfolioConstructionService,
    PortfolioPolicy,
    PortfolioStressTestService,
    RankedCandidate,
    StressScenario,
    StressStatus,
    build_operator_review_packet,
    build_stage7_acceptance,
)


def _candidate(
    candidate_id: str,
    symbol: str,
    adapter_id: MarketAdapterId,
    rank: int,
    score: str,
    asset_class: str,
    industry: str,
    theme: str,
    price: str,
    lot_size: int,
    current_weight: str,
    correlations: dict[str, str] | None = None,
    liquidity: str = "50000000",
    drawdown: str = "-0.20",
) -> RankedCandidate:
    return RankedCandidate(
        candidate_id=candidate_id,
        symbol=symbol,
        market_adapter_id=adapter_id,
        adapter_status=AdapterStatus.READY_FOR_OPERATOR_REVIEW,
        rank=rank,
        deterministic_score=Decimal(score),
        asset_class=asset_class,
        industry=industry,
        theme=theme,
        factor_exposures={"quality": Decimal("0.3"), "momentum": Decimal("0.2")},
        pair_correlations={
            key: Decimal(value) for key, value in (correlations or {}).items()
        },
        beta=Decimal("0.8"),
        annualized_volatility=Decimal("0.20"),
        average_daily_value=Decimal(liquidity),
        max_drawdown=Decimal(drawdown),
        price=Decimal(price),
        lot_size=lot_size,
        current_paper_weight=Decimal(current_weight),
        evidence_ids=(f"evidence-{candidate_id}",),
    )


def _candidates() -> tuple[RankedCandidate, ...]:
    return (
        _candidate(
            "candidate-aapl", "AAPL", MarketAdapterId.US_EQUITY, 1, "100",
            "US_EQUITY", "TECH", "MEGA_CAP", "200", 1, "0.30",
            {"0700.HK": "0.40", "BTCUSDT": "0.20"},
        ),
        _candidate(
            "candidate-0700", "0700.HK", MarketAdapterId.HONG_KONG_EQUITY,
            2, "80", "HK_EQUITY", "COMMUNICATION", "PLATFORM", "50", 100,
            "0.30", {"BTCUSDT": "0.15"},
        ),
        _candidate(
            "candidate-btc", "BTCUSDT", MarketAdapterId.DIGITAL_ASSET, 3, "60",
            "DIGITAL_ASSET", "CRYPTO", "BTC", "65000", 1, "0.30",
        ),
    )


def _policy(**updates: object) -> PortfolioPolicy:
    values: dict[str, object] = {
        "policy_id": "portfolio-policy-a",
        "version": "v1",
        "evidence_ids": ("policy-evidence-a",),
        "target_notional": Decimal("1000000"),
        "risk_budget_fraction": Decimal("0.90"),
        "max_single_weight": Decimal("0.40"),
        "max_industry_weight": Decimal("0.50"),
        "max_theme_weight": Decimal("0.50"),
        "max_factor_exposure": Decimal("0.80"),
        "max_pair_correlation": Decimal("0.85"),
        "max_portfolio_beta": Decimal("1.20"),
        "max_portfolio_volatility": Decimal("0.35"),
        "min_average_daily_value": Decimal("1000000"),
        "max_drawdown": Decimal("-0.40"),
        "max_turnover": Decimal("0.60"),
        "max_liquidity_participation": Decimal("0.10"),
        "transaction_cost_bps": Decimal("10"),
        "max_transaction_cost": Decimal("5000"),
        "max_stress_loss_fraction": Decimal("0.20"),
    }
    values.update(updates)
    return PortfolioPolicy(**values)


def _request(
    candidates: tuple[RankedCandidate, ...] | None = None,
    policy: PortfolioPolicy | None = None,
) -> PortfolioConstructionRequest:
    return PortfolioConstructionRequest(
        request_id="portfolio-request-a",
        correlation_id="portfolio-correlation-a",
        ranking_artifact_id="ranking-artifact-a",
        candidates=candidates or _candidates(),
        policy=policy or _policy(),
    )


def _scenario(**updates: object) -> StressScenario:
    values: dict[str, object] = {
        "scenario_id": "broad-risk-off",
        "version": "v1",
        "evidence_ids": ("scenario-evidence-a",),
        "market_return_shock": Decimal("-0.05"),
        "volatility_multiplier": Decimal("1.5"),
        "liquidity_haircut": Decimal("0.25"),
        "asset_class_shocks": {
            "US_EQUITY": Decimal("-0.02"),
            "HK_EQUITY": Decimal("-0.03"),
            "DIGITAL_ASSET": Decimal("-0.08"),
        },
        "industry_shocks": {},
        "theme_shocks": {},
        "factor_shocks": {"momentum": Decimal("-0.02")},
    }
    values.update(updates)
    return StressScenario(**values)


def _constructed(policy: PortfolioPolicy | None = None):
    return PortfolioConstructionService().construct(_request(policy=policy))


def test_d1_boundary_rejects_live_positions_rebalance_orders_and_execution():
    prohibited = (
        "position_read_allowed", "broker_connection_allowed",
        "automatic_rebalance_allowed", "order_path_allowed",
        "real_execution_allowed", "live_model_invocation_allowed",
    )
    for field_name in prohibited:
        with pytest.raises(ValueError, match="prohibited portfolio"):
            replace(PORTFOLIO_STAGE_7_BOUNDARY, **{field_name: True})


def test_d1_ranked_candidates_must_preserve_unique_order():
    candidates = tuple(reversed(_candidates()))
    with pytest.raises(ValueError, match="rank order"):
        _request(candidates=candidates)


def test_d2_deterministic_allocation_uses_score_order_and_risk_budget():
    outcome = _constructed()
    weights = {item.symbol: item.proposed_weight for item in outcome.positions}
    assert outcome.status is ConstructionStatus.READY_FOR_STRESS_TEST
    assert weights == {
        "AAPL": Decimal("0.375"),
        "0700.HK": Decimal("0.300"),
        "BTCUSDT": Decimal("0.225"),
    }
    assert outcome.cash_weight == Decimal("0.100")


def test_d2_paper_sizing_turnover_and_cost_are_deterministic():
    outcome = _constructed()
    quantities = {item.symbol: item.paper_quantity for item in outcome.positions}
    assert quantities == {"AAPL": 1875, "0700.HK": 6000, "BTCUSDT": 3}
    assert outcome.turnover == Decimal("0.075")
    assert outcome.estimated_transaction_cost == Decimal("75.000")


def test_d3_industry_concentration_breach_fails_closed():
    outcome = _constructed(_policy(max_industry_weight=Decimal("0.25")))
    assert outcome.status is ConstructionStatus.BLOCKED
    assert any(code.startswith("industry-concentration-breach") for code in outcome.reason_codes)


def test_d3_factor_concentration_breach_fails_closed():
    outcome = _constructed(_policy(max_factor_exposure=Decimal("0.10")))
    assert outcome.status is ConstructionStatus.BLOCKED
    assert "factor-concentration-breach-quality" in outcome.reason_codes


def test_d3_pair_correlation_breach_fails_closed():
    outcome = _constructed(_policy(max_pair_correlation=Decimal("0.30")))
    assert outcome.status is ConstructionStatus.BLOCKED
    assert "correlation-breach-AAPL-0700.HK" in outcome.reason_codes


def test_d3_liquidity_and_drawdown_exclusions_remain_visible():
    candidates = list(_candidates())
    candidates[2] = replace(
        candidates[2],
        average_daily_value=Decimal("100"),
        max_drawdown=Decimal("-0.80"),
    )
    outcome = PortfolioConstructionService().construct(_request(tuple(candidates)))
    assert "excluded-BTCUSDT-liquidity" in outcome.reason_codes
    assert {item.symbol for item in outcome.positions} == {"AAPL", "0700.HK"}


def test_d3_turnover_and_cost_limits_fail_closed():
    outcome = _constructed(
        _policy(max_turnover=Decimal("0.01"), max_transaction_cost=Decimal("10"))
    )
    assert outcome.status is ConstructionStatus.BLOCKED
    assert {"portfolio-turnover-breach", "transaction-cost-breach"}.issubset(
        outcome.reason_codes
    )


def test_d4_versioned_stress_scenario_calculates_loss_attribution():
    stress = PortfolioStressTestService().evaluate(_constructed(), (_scenario(),))
    result = stress.scenario_results[0]
    assert stress.status is StressStatus.PASS
    assert result.loss_amount > 0
    assert set(result.position_loss_attribution) == {"AAPL", "0700.HK", "BTCUSDT"}
    assert result.stressed_volatility == Decimal("0.27000")


def test_d4_stress_loss_budget_breach_fails_closed():
    scenario = _scenario(market_return_shock=Decimal("-0.50"))
    stress = PortfolioStressTestService().evaluate(
        _constructed(_policy(max_stress_loss_fraction=Decimal("0.10"))),
        (scenario,),
    )
    assert stress.status is StressStatus.BLOCKED
    assert "stress-loss-budget-breach" in stress.scenario_results[0].reason_codes


def test_d4_stressed_liquidity_breach_is_visible():
    scenario = _scenario(liquidity_haircut=Decimal("0.99"))
    stress = PortfolioStressTestService().evaluate(_constructed(), (scenario,))
    assert stress.status is StressStatus.BLOCKED
    assert any(
        code.startswith("stressed-liquidity-breach")
        for code in stress.scenario_results[0].reason_codes
    )


def test_d5_review_packet_preserves_ranked_inputs_and_paper_boundary():
    construction = _constructed()
    stress = PortfolioStressTestService().evaluate(construction, (_scenario(),))
    packet = build_operator_review_packet(stress)
    assert len(packet.payload["original_ranked_candidates"]) == 3
    assert packet.payload["paper_position_proposal_only"] is True
    assert packet.payload["operator_review_required"] is True
    assert packet.payload["automatic_rebalance_allowed"] is False
    assert packet.payload["real_execution_allowed"] is False
    with pytest.raises(TypeError):
        packet.payload["stress_status"] = "TAMPERED"


def test_d6_acceptance_links_both_apps_and_requires_operator_review():
    construction = _constructed()
    stress = PortfolioStressTestService().evaluate(construction, (_scenario(),))
    acceptance = build_stage7_acceptance(stress, build_operator_review_packet(stress))
    assert acceptance.status == "PASS"
    assert acceptance.construction_app_id == "PORTFOLIO-CONSTRUCTION-APP-1"
    assert acceptance.stress_app_id == "PORTFOLIO-STRESS-TEST-APP-1"
    assert acceptance.operator_review_required is True


def test_d6_acceptance_rejects_blocked_construction():
    construction = _constructed(_policy(max_industry_weight=Decimal("0.10")))
    stress = PortfolioStressTestService().evaluate(construction, (_scenario(),))
    with pytest.raises(ValueError, match="construction is not ready"):
        build_stage7_acceptance(stress, build_operator_review_packet(stress))
