import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from stock_app.contracts.limit_up_potential import HIGH_POTENTIAL
from stock_app.contracts.limit_up_potential import REJECTED_LEVEL
from stock_app.contracts.limit_up_potential import WATCH_ONLY_LEVEL
from stock_app.contracts.limit_up_potential import build_limit_up_potential_package
from stock_app.contracts.limit_up_potential import evaluate_limit_up_potential


def high_record():
    return {
        "symbol": "600000",
        "name": "Sample High",
        "trading_status": "TRADING",
        "is_st": False,
        "listing_days": 5000,
        "turnover_rate": 8.0,
        "amount": 180000000,
        "open": 10.0,
        "high": 10.85,
        "low": 9.9,
        "close": 10.8,
        "prev_close": 10.0,
        "limit_up_price": 11.0,
        "volume": 3000000,
        "avg_volume_5d": 1000000,
        "avg_turnover_5d": 3.0,
        "high_20d": 10.7,
        "sector_code": "BK001",
        "sector_name": "AI Computing",
        "theme_tags": ["AI", "Computing"],
        "sector_strength_score": 88,
        "theme_heat_score": 82,
        "market_breadth_score": 76,
        "dragon_tiger_signal": True,
        "northbound_flow_score": 80,
        "etf_flow_score": 70,
        "large_trade_proxy_score": 85,
        "amount_expansion_score": 75,
        "sector_fund_heat_score": 72,
        "data_quality_state": "PASS_STRICT",
        "data_sources": ["DATA-APP", "PUBLIC_FIXTURE"],
    }


def test_high_record_gets_high_potential_without_trade_instruction():
    result = evaluate_limit_up_potential(high_record())
    assert result["potential_level"] == HIGH_POTENTIAL
    assert result["limit_up_potential_score"] >= 75
    assert "LIMIT_UP_POTENTIAL_HIGH" in result["reason_codes"]
    assert result["score_breakdown"]["final_score"] == result["limit_up_potential_score"]
    assert result["buy_instruction_allowed"] is False
    assert result["sell_instruction_allowed"] is False
    assert result["guaranteed_limit_up_claim_allowed"] is False
    assert result["real_action_blocked"] is True


def test_pass_limited_record_is_watch_only_even_with_good_signals():
    record = high_record()
    record["data_quality_state"] = "PASS_LIMITED"
    result = evaluate_limit_up_potential(record)
    assert result["potential_level"] == WATCH_ONLY_LEVEL
    assert "PASS_LIMITED_CANNOT_HIGH_RANK" in result["risk_flags"]
    assert result["operator_review_required"] is True


def test_st_record_is_rejected():
    record = high_record()
    record["is_st"] = True
    result = evaluate_limit_up_potential(record)
    assert result["potential_level"] == REJECTED_LEVEL
    assert "IS_ST_OR_RISK_WARNING" in result["risk_flags"]


def test_fail_quarantine_record_is_rejected_with_zero_or_low_score():
    record = high_record()
    record["data_quality_state"] = "FAIL_QUARANTINE"
    result = evaluate_limit_up_potential(record)
    assert result["potential_level"] == REJECTED_LEVEL
    assert "DATA_QUALITY_QUARANTINE" in result["risk_flags"]


def test_score_breakdown_contains_required_components():
    result = evaluate_limit_up_potential(high_record())
    breakdown = result["score_breakdown"]
    assert set(breakdown.keys()) == {
        "data_quality_score",
        "base_filter_score",
        "sector_theme_score",
        "volume_price_score",
        "fund_flow_proxy_score",
        "risk_penalty",
        "raw_score",
        "final_score",
    }


def test_result_contains_required_output_fields():
    result = evaluate_limit_up_potential(high_record())
    assert "score_breakdown" in result
    assert "reason_codes" in result
    assert "risk_flags" in result
    assert "data_quality_state" in result
    assert "confidence_level" in result
    assert "data_sources" in result
    assert result["operator_review_required"] is True


def test_build_limit_up_potential_package_counts_buckets():
    high = high_record()
    watch = high_record()
    watch["symbol"] = "000001"
    watch["data_quality_state"] = "PASS_LIMITED"
    rejected = high_record()
    rejected["symbol"] = "300000"
    rejected["trading_status"] = "SUSPENDED"

    result = build_limit_up_potential_package([high, watch, rejected])
    assert result["app"] == "STOCK-APP"
    assert result["contract_version"] == "STOCK_APP_LIMIT_UP_POTENTIAL_V1"
    assert result["input_count"] == 3
    assert result["high_potential_count"] == 1
    assert result["watch_only_count"] == 1
    assert result["rejected_count"] == 1
    assert result["buy_instruction_allowed"] is False
    assert result["guaranteed_limit_up_claim_allowed"] is False
    assert result["paper_only"] is True
    assert result["real_action_blocked"] is True
