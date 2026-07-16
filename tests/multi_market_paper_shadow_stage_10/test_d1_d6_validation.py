from dataclasses import replace
from decimal import Decimal
from types import MappingProxyType

import pytest

from apps.fcf_web_console_app_1 import (
    FCFWebConsoleApplication,
    WebConsoleSnapshot,
)
from apps.multi_market_adapters_stage_6 import AdapterStatus, MarketAdapterId
from apps.multi_market_paper_shadow_stage_10 import (
    MULTI_MARKET_PAPER_SHADOW_BOUNDARY,
    MultiMarketPaperShadowValidationService,
    MultiMarketValidationRequest,
    PaperMarketValidation,
    ShadowMarketObservation,
    ShadowMaturity,
    ValidationStatus,
    build_console_sections,
    build_stage10_acceptance,
)


def _paper(adapter_id, **overrides):
    values = {
        "adapter_id": adapter_id,
        "adapter_status": AdapterStatus.READY_FOR_OPERATOR_REVIEW,
        "window_id": f"paper-{adapter_id.name.lower()}",
        "start_time_utc": "2026-01-01T00:00:00Z",
        "end_time_utc": "2026-03-31T00:00:00Z",
        "paper_notional": Decimal("100000"),
        "candidate_return": Decimal("0.10"),
        "benchmark_return": Decimal("0.05"),
        "maximum_loss_fraction": Decimal("0.08"),
        "turnover": Decimal("0.20"),
        "transaction_cost": Decimal("125"),
        "exposure_breach_codes": (),
        "evidence_ids": (f"paper-evidence-{adapter_id.name.lower()}",),
        "currency_context_id": f"currency-{adapter_id.name.lower()}",
        "calendar_id": f"calendar-{adapter_id.name.lower()}",
    }
    values.update(overrides)
    return PaperMarketValidation(**values)


def _shadow(adapter_id, **overrides):
    values = {
        "adapter_id": adapter_id,
        "decision_time_utc": "2026-04-01T00:00:00Z",
        "observation_time_utc": "2026-04-30T00:00:00Z",
        "maturity": ShadowMaturity.MATURE,
        "expected_return": Decimal("0.02"),
        "observed_return": Decimal("0.03"),
        "evidence_ids": (f"shadow-evidence-{adapter_id.name.lower()}",),
        "observation_artifact_id": f"shadow-artifact-{adapter_id.name.lower()}",
    }
    values.update(overrides)
    return ShadowMarketObservation(**values)


def _request(paper=None, shadow=None):
    return MultiMarketValidationRequest(
        request_id="stage10-request",
        correlation_id="stage10-correlation",
        portfolio_artifact_id="portfolio-stage7",
        benchmark_artifact_id="benchmark-registered",
        policy_version="policy-v1",
        operator_trigger_id="operator-trigger-1",
        paper_markets=tuple(paper or (_paper(item) for item in MarketAdapterId)),
        shadow_markets=tuple(shadow or (_shadow(item) for item in MarketAdapterId)),
    )


def _evaluate(request=None):
    return MultiMarketPaperShadowValidationService().evaluate(
        request or _request()
    )


def test_d1_boundary_preserves_authorities_and_prohibitions():
    assert MULTI_MARKET_PAPER_SHADOW_BOUNDARY.paper_only is True
    assert MULTI_MARKET_PAPER_SHADOW_BOUNDARY.registered_artifact_only is True
    assert MULTI_MARKET_PAPER_SHADOW_BOUNDARY.deterministic_authority is True
    assert MULTI_MARKET_PAPER_SHADOW_BOUNDARY.model_invocation_allowed is False
    assert MULTI_MARKET_PAPER_SHADOW_BOUNDARY.real_execution_allowed is False
    assert MULTI_MARKET_PAPER_SHADOW_BOUNDARY.automatic_learning_allowed is False


def test_d1_all_six_market_identities_are_required_by_acceptance():
    acceptance = build_stage10_acceptance()
    assert acceptance.status == "D1_D6_ACCEPTED"
    assert set(acceptance.market_ids) == {item.value for item in MarketAdapterId}


def test_d1_shadow_rejects_lookahead_and_pending_result():
    with pytest.raises(ValueError, match="cannot precede"):
        _shadow(
            MarketAdapterId.DIGITAL_ASSET,
            observation_time_utc="2026-03-31T00:00:00Z",
        )
    with pytest.raises(ValueError, match="pending"):
        _shadow(
            MarketAdapterId.DIGITAL_ASSET,
            maturity=ShadowMaturity.PENDING,
            observed_return=Decimal("0.01"),
        )


def test_d2_complete_six_market_coverage_passes_for_review():
    outcome = _evaluate()
    assert outcome.status is ValidationStatus.PASS_REVIEW_REQUIRED
    assert len(outcome.findings) == 6
    assert outcome.paper_market_coverage == Decimal("1")
    assert outcome.shadow_market_coverage == Decimal("1")
    assert outcome.mature_shadow_coverage == Decimal("1")


def test_d2_missing_market_fails_closed():
    paper = tuple(_paper(item) for item in MarketAdapterId if item is not MarketAdapterId.FUTURES)
    outcome = _evaluate(_request(paper=paper))
    assert outcome.status is ValidationStatus.BLOCKED_REVIEW_REQUIRED
    assert outcome.paper_market_coverage == Decimal("5") / Decimal("6")
    assert "missing-paper-market-coverage" in outcome.reason_codes


def test_d2_blocked_adapter_and_data_quality_fail_closed():
    paper = tuple(
        _paper(
            item,
            adapter_status=(
                AdapterStatus.BLOCKED
                if item is MarketAdapterId.CHINA_A_SHARE
                else AdapterStatus.READY_FOR_OPERATOR_REVIEW
            ),
            data_quality_state=(
                "BLOCKED" if item is MarketAdapterId.CHINA_A_SHARE else "PASS"
            ),
        )
        for item in MarketAdapterId
    )
    outcome = _evaluate(_request(paper=paper))
    finding = next(
        item
        for item in outcome.findings
        if item.adapter_id is MarketAdapterId.CHINA_A_SHARE
    )
    assert outcome.status is ValidationStatus.BLOCKED_REVIEW_REQUIRED
    assert "market-adapter-blocked" in finding.reason_codes
    assert "data-quality-blocked" in finding.reason_codes


def test_d3_paper_metrics_are_deterministic():
    outcome = _evaluate()
    assert outcome.aggregate_paper_excess_return == Decimal("0.05")
    assert all(
        item.paper_excess_return == Decimal("0.05")
        for item in outcome.findings
    )


def test_d3_underperformance_and_exposure_breach_are_visible():
    paper = tuple(
        _paper(
            item,
            candidate_return=(
                Decimal("-0.02")
                if item is MarketAdapterId.US_EQUITY
                else Decimal("0.10")
            ),
            exposure_breach_codes=(
                ("single-weight-breach",)
                if item is MarketAdapterId.US_EQUITY
                else ()
            ),
        )
        for item in MarketAdapterId
    )
    outcome = _evaluate(_request(paper=paper))
    finding = next(
        item
        for item in outcome.findings
        if item.adapter_id is MarketAdapterId.US_EQUITY
    )
    assert outcome.status is ValidationStatus.DEGRADED_REVIEW_REQUIRED
    assert "paper-underperformed-benchmark" in finding.reason_codes
    assert "single-weight-breach" in finding.reason_codes


def test_d3_cross_market_disagreement_is_visible_and_degraded():
    paper = tuple(
        _paper(
            item,
            candidate_return=(
                Decimal("-0.10")
                if item is MarketAdapterId.DIGITAL_ASSET
                else Decimal("0.10")
            ),
        )
        for item in MarketAdapterId
    )
    outcome = _evaluate(_request(paper=paper))
    assert outcome.disagreement_visible is True
    assert outcome.status is ValidationStatus.DEGRADED_REVIEW_REQUIRED
    assert "cross-market-paper-disagreement" in outcome.reason_codes


def test_d4_pending_shadow_window_is_degraded_not_fabricated():
    shadow = tuple(
        _shadow(
            item,
            observation_time_utc="2026-04-01T00:00:00Z",
            maturity=ShadowMaturity.PENDING,
            observed_return=None,
        )
        if item is MarketAdapterId.FUTURES
        else _shadow(item)
        for item in MarketAdapterId
    )
    outcome = _evaluate(_request(shadow=shadow))
    assert outcome.status is ValidationStatus.DEGRADED_REVIEW_REQUIRED
    assert outcome.mature_shadow_coverage == Decimal("5") / Decimal("6")
    finding = next(
        item for item in outcome.findings if item.adapter_id is MarketAdapterId.FUTURES
    )
    assert finding.shadow_error is None
    assert "shadow-window-pending" in finding.reason_codes


def test_d4_historical_forward_overlap_is_blocked():
    shadow = tuple(
        _shadow(
            item,
            decision_time_utc="2026-03-01T00:00:00Z",
            observation_time_utc="2026-04-01T00:00:00Z",
        )
        if item is MarketAdapterId.GOLD_COMMODITY
        else _shadow(item)
        for item in MarketAdapterId
    )
    outcome = _evaluate(_request(shadow=shadow))
    assert outcome.status is ValidationStatus.BLOCKED_REVIEW_REQUIRED
    assert "historical-forward-window-overlap" in outcome.reason_codes


def test_d4_shadow_direction_contradiction_is_preserved():
    shadow = tuple(
        _shadow(
            item,
            observed_return=(
                Decimal("-0.03")
                if item is MarketAdapterId.HONG_KONG_EQUITY
                else Decimal("0.03")
            ),
        )
        for item in MarketAdapterId
    )
    outcome = _evaluate(_request(shadow=shadow))
    assert outcome.status is ValidationStatus.DEGRADED_REVIEW_REQUIRED
    assert "shadow-direction-contradiction" in outcome.reason_codes


def test_d5_operator_packet_is_immutable_and_never_transitions_authority():
    outcome = _evaluate()
    packet = outcome.operator_review_packet
    with pytest.raises(TypeError):
        packet["status"] = "APPROVED"
    assert packet["operator_review_required"] is True
    assert packet["automatic_approval_allowed"] is False
    assert outcome.automatic_promotion_allowed is False
    assert outcome.automatic_learning_allowed is False
    assert outcome.real_execution_used is False


def test_d5_stale_and_degraded_market_state_remain_visible():
    paper = tuple(
        _paper(
            item,
            freshness_state=(
                "STALE" if item is MarketAdapterId.CHINA_A_SHARE else "CURRENT"
            ),
            data_quality_state=(
                "DEGRADED" if item is MarketAdapterId.CHINA_A_SHARE else "PASS"
            ),
        )
        for item in MarketAdapterId
    )
    outcome = _evaluate(_request(paper=paper))
    assert outcome.status is ValidationStatus.DEGRADED_REVIEW_REQUIRED
    assert "data-freshness-review" in outcome.reason_codes
    assert "data-quality-degraded" in outcome.reason_codes


def test_d6_console_sections_render_in_stage_8_product_pages():
    outcome = _evaluate()
    sections = build_console_sections(outcome)
    snapshot = WebConsoleSnapshot(
        correlation_id=outcome.request.correlation_id,
        sections=sections,
        source_artifact_ids=(
            outcome.request.portfolio_artifact_id,
            outcome.request.benchmark_artifact_id,
        ),
    )
    application = FCFWebConsoleApplication(snapshot)
    portfolio = application.dispatch("GET", "/portfolio").body.decode("utf-8")
    paper = application.dispatch("GET", "/paper-portfolio").body.decode("utf-8")
    assert "multi_market_validation" in portfolio
    assert "PASS_REVIEW_REQUIRED" in portfolio
    assert "paper_portfolio_validation" in paper
    assert "shadow_market_observation" in paper


def test_d6_console_section_payloads_remain_immutable():
    sections = build_console_sections(_evaluate())
    assert isinstance(sections, MappingProxyType)
    with pytest.raises(TypeError):
        sections["new"] = ()


def test_d6_next_phase_is_learning_p0_p3_not_dify_runtime():
    acceptance = build_stage10_acceptance()
    assert acceptance.next_phase == "CONTROLLED_LEARNING_BACKTESTING_P0_P3"
