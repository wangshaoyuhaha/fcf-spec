import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from stock_app.contracts.fund_flow_proxy import MEDIUM_PUBLIC_FLOW
from stock_app.contracts.fund_flow_proxy import NO_PUBLIC_FLOW
from stock_app.contracts.fund_flow_proxy import STRONG_PUBLIC_FLOW
from stock_app.contracts.fund_flow_proxy import WEAK_PUBLIC_FLOW
from stock_app.contracts.fund_flow_proxy import build_public_fund_flow_proxy_package
from stock_app.contracts.fund_flow_proxy import evaluate_public_fund_flow_proxy


def strong_record():
    return {
        "symbol": "600000",
        "name": "Sample Strong",
        "dragon_tiger_signal": True,
        "northbound_flow_score": 80,
        "etf_flow_score": 70,
        "large_trade_proxy_score": 85,
        "amount_expansion_score": 75,
        "sector_fund_heat_score": 72,
        "data_quality_state": "PASS_STRICT",
    }


def test_strong_public_flow_uses_only_public_signals():
    result = evaluate_public_fund_flow_proxy(strong_record())
    assert result["fund_flow_proxy_level"] == STRONG_PUBLIC_FLOW
    assert result["confidence_level"] == "HIGH"
    assert "DRAGON_TIGER_SIGNAL" in result["reason_codes"]
    assert "NORTHBOUND_SIGNAL" in result["reason_codes"]
    assert "LARGE_TRADE_PROXY_SIGNAL" in result["reason_codes"]
    assert result["public_signal_only"] is True
    assert result["hidden_position_claim_allowed"] is False
    assert result["real_action_blocked"] is True


def test_pass_limited_flow_is_not_high_ranked():
    record = strong_record()
    record["data_quality_state"] = "PASS_LIMITED"
    result = evaluate_public_fund_flow_proxy(record)
    assert result["fund_flow_proxy_level"] == MEDIUM_PUBLIC_FLOW
    assert "DATA_QUALITY_LIMITED" in result["risk_flags"]
    assert "PASS_LIMITED_CANNOT_HIGH_RANK" in result["risk_flags"]


def test_fail_quarantine_blocks_public_flow_scoring():
    record = strong_record()
    record["data_quality_state"] = "FAIL_QUARANTINE"
    result = evaluate_public_fund_flow_proxy(record)
    assert result["fund_flow_proxy_score"] == 0.0
    assert result["fund_flow_proxy_level"] == NO_PUBLIC_FLOW
    assert "DATA_QUALITY_QUARANTINE" in result["risk_flags"]


def test_no_public_signal_adds_weak_and_no_confirmation_flags():
    record = strong_record()
    record["dragon_tiger_signal"] = False
    record["northbound_flow_score"] = 0
    record["etf_flow_score"] = 0
    record["large_trade_proxy_score"] = 0
    record["amount_expansion_score"] = 0
    record["sector_fund_heat_score"] = 0
    result = evaluate_public_fund_flow_proxy(record)
    assert result["fund_flow_proxy_level"] == NO_PUBLIC_FLOW
    assert "NO_FUND_FLOW_CONFIRMATION" in result["risk_flags"]
    assert "PUBLIC_SIGNAL_WEAK" in result["risk_flags"]


def test_string_positive_signal_is_accepted():
    record = strong_record()
    record["dragon_tiger_signal"] = "positive"
    result = evaluate_public_fund_flow_proxy(record)
    assert result["dragon_tiger_signal"] is True


def test_scores_are_clamped_to_safe_range():
    record = strong_record()
    record["northbound_flow_score"] = 200
    record["etf_flow_score"] = -10
    result = evaluate_public_fund_flow_proxy(record)
    assert result["northbound_flow_score"] == 100.0
    assert result["etf_flow_score"] == 0.0


def test_build_public_fund_flow_proxy_package_counts_levels():
    strong = strong_record()
    medium = strong_record()
    medium["symbol"] = "000001"
    medium["northbound_flow_score"] = 60
    medium["etf_flow_score"] = 20
    medium["large_trade_proxy_score"] = 50
    medium["amount_expansion_score"] = 20
    medium["sector_fund_heat_score"] = 30
    weak = strong_record()
    weak["symbol"] = "300000"
    weak["dragon_tiger_signal"] = False
    weak["northbound_flow_score"] = 20
    weak["etf_flow_score"] = 10
    weak["large_trade_proxy_score"] = 20
    weak["amount_expansion_score"] = 10
    weak["sector_fund_heat_score"] = 10

    result = build_public_fund_flow_proxy_package([strong, medium, weak])
    assert result["app"] == "STOCK-APP"
    assert result["contract_version"] == "STOCK_APP_FUND_FLOW_PROXY_V1"
    assert result["input_count"] == 3
    assert result["strong_public_flow_count"] == 1
    assert result["medium_public_flow_count"] == 1
    assert result["weak_public_flow_count"] == 1
    assert result["public_signal_only"] is True
    assert result["hidden_position_claim_allowed"] is False
    assert result["paper_only"] is True
    assert result["real_action_blocked"] is True
