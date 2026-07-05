import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from stock_app.contracts.base_candidate_filter import BASE_CANDIDATE
from stock_app.contracts.base_candidate_filter import REJECTED
from stock_app.contracts.base_candidate_filter import WATCH_ONLY
from stock_app.contracts.base_candidate_filter import build_base_candidate_pool
from stock_app.contracts.base_candidate_filter import evaluate_base_candidate


def strict_record():
    return {
        "symbol": "600000",
        "name": "Sample Bank",
        "trading_status": "TRADING",
        "is_st": False,
        "listing_days": 5000,
        "turnover_rate": 2.5,
        "amount": 120000000,
        "close": 10.5,
        "limit_up_price": 11.55,
        "data_quality_state": "PASS_STRICT",
    }


def test_pass_strict_record_becomes_base_candidate():
    result = evaluate_base_candidate(strict_record())
    assert result["decision"] == BASE_CANDIDATE
    assert result["base_filter_pass"] is True
    assert "DATA_QUALITY_PASS_STRICT" in result["reason_codes"]
    assert "LIQUIDITY_OK" in result["reason_codes"]
    assert result["operator_review_required"] is True
    assert result["real_action_blocked"] is True


def test_pass_limited_record_becomes_watch_only():
    record = strict_record()
    record["data_quality_state"] = "PASS_LIMITED"
    result = evaluate_base_candidate(record)
    assert result["decision"] == WATCH_ONLY
    assert result["base_filter_pass"] is True
    assert "DATA_QUALITY_LIMITED" in result["risk_flags"]


def test_fail_quarantine_record_is_rejected():
    record = strict_record()
    record["data_quality_state"] = "FAIL_QUARANTINE"
    result = evaluate_base_candidate(record)
    assert result["decision"] == REJECTED
    assert "fail_quarantine" in result["excluded_reasons"]
    assert "DATA_QUALITY_QUARANTINE" in result["risk_flags"]


def test_st_or_suspended_record_is_rejected():
    record = strict_record()
    record["is_st"] = True
    record["trading_status"] = "SUSPENDED"
    result = evaluate_base_candidate(record)
    assert result["decision"] == REJECTED
    assert "st_or_risk_warning" in result["excluded_reasons"]
    assert "not_trading_active" in result["excluded_reasons"]


def test_missing_required_fields_are_rejected():
    result = evaluate_base_candidate({"symbol": "600000"})
    assert result["decision"] == REJECTED
    assert result["base_filter_pass"] is False
    assert "MISSING_REQUIRED_FIELDS" in result["reason_codes"]
    assert "DATA_QUALITY_LIMITED" in result["risk_flags"]


def test_build_base_candidate_pool_counts_all_buckets():
    strict = strict_record()
    limited = strict_record()
    limited["symbol"] = "000001"
    limited["data_quality_state"] = "PASS_LIMITED"
    rejected = strict_record()
    rejected["symbol"] = "300000"
    rejected["is_st"] = True

    result = build_base_candidate_pool([strict, limited, rejected])
    assert result["app"] == "STOCK-APP"
    assert result["contract_version"] == "STOCK_APP_BASE_FILTER_V1"
    assert result["input_count"] == 3
    assert result["base_candidate_count"] == 1
    assert result["watch_only_count"] == 1
    assert result["rejected_count"] == 1
    assert result["paper_only"] is True
    assert result["real_action_blocked"] is True
