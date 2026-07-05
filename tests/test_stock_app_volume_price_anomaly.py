import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from stock_app.contracts.volume_price_anomaly import MEDIUM_ANOMALY
from stock_app.contracts.volume_price_anomaly import NO_ANOMALY
from stock_app.contracts.volume_price_anomaly import STRONG_ANOMALY
from stock_app.contracts.volume_price_anomaly import build_volume_price_anomaly_package
from stock_app.contracts.volume_price_anomaly import evaluate_volume_price_anomaly


def strong_record():
    return {
        "symbol": "600000",
        "name": "Sample Strong",
        "close": 10.8,
        "prev_close": 10.0,
        "high": 10.85,
        "low": 9.9,
        "limit_up_price": 11.0,
        "volume": 3000000,
        "avg_volume_5d": 1000000,
        "turnover_rate": 8.0,
        "avg_turnover_5d": 3.0,
        "high_20d": 10.7,
        "data_quality_state": "PASS_STRICT",
    }


def test_strong_volume_price_record_gets_strong_anomaly():
    result = evaluate_volume_price_anomaly(strong_record())
    assert result["volume_price_level"] == STRONG_ANOMALY
    assert result["confidence_level"] == "HIGH"
    assert "NEAR_LIMIT_UP_PRICE" in result["reason_codes"]
    assert "VOLUME_EXPANSION" in result["reason_codes"]
    assert "TURNOVER_EXPANSION" in result["reason_codes"]
    assert "CLOSE_NEAR_HIGH" in result["reason_codes"]
    assert "PRICE_BREAKOUT" in result["reason_codes"]
    assert result["real_action_blocked"] is True


def test_pass_limited_discounts_volume_price_score():
    record = strong_record()
    record["data_quality_state"] = "PASS_LIMITED"
    result = evaluate_volume_price_anomaly(record)
    assert result["volume_price_level"] == MEDIUM_ANOMALY
    assert "DATA_QUALITY_LIMITED" in result["risk_flags"]
    assert "PASS_LIMITED_CANNOT_HIGH_RANK" in result["risk_flags"]


def test_fail_quarantine_blocks_volume_price_scoring():
    record = strong_record()
    record["data_quality_state"] = "FAIL_QUARANTINE"
    result = evaluate_volume_price_anomaly(record)
    assert result["volume_price_score"] == 0.0
    assert result["volume_price_level"] == NO_ANOMALY
    assert "DATA_QUALITY_QUARANTINE" in result["risk_flags"]


def test_abnormal_price_adds_price_risk_flag():
    record = strong_record()
    record["close"] = 0
    result = evaluate_volume_price_anomaly(record)
    assert "PRICE_ABNORMAL_RISK" in result["risk_flags"]


def test_missing_volume_and_turnover_baseline_adds_risk_flags():
    record = strong_record()
    record["avg_volume_5d"] = 0
    record["avg_turnover_5d"] = 0
    result = evaluate_volume_price_anomaly(record)
    assert "MISSING_VOLUME_BASELINE" in result["risk_flags"]
    assert "MISSING_TURNOVER_BASELINE" in result["risk_flags"]


def test_high_turnover_and_limit_up_too_close_add_risk_flags():
    record = strong_record()
    record["close"] = 10.99
    record["limit_up_price"] = 11.0
    record["turnover_rate"] = 25.0
    result = evaluate_volume_price_anomaly(record)
    assert "LIMIT_UP_TOO_CLOSE_RISK" in result["risk_flags"]
    assert "HIGH_TURNOVER_RISK" in result["risk_flags"]


def test_build_volume_price_anomaly_package_counts_levels():
    strong = strong_record()
    medium = strong_record()
    medium["symbol"] = "000001"
    medium["volume"] = 1600000
    medium["turnover_rate"] = 3.8
    medium["high_20d"] = 12.0
    weak = strong_record()
    weak["symbol"] = "300000"
    weak["close"] = 10.4
    weak["high"] = 10.45
    weak["volume"] = 1500000
    weak["turnover_rate"] = 2.0
    weak["high_20d"] = 12.0

    result = build_volume_price_anomaly_package([strong, medium, weak])
    assert result["app"] == "STOCK-APP"
    assert result["contract_version"] == "STOCK_APP_VOLUME_PRICE_V1"
    assert result["input_count"] == 3
    assert result["strong_anomaly_count"] == 1
    assert result["medium_anomaly_count"] == 1
    assert result["weak_anomaly_count"] == 1
    assert result["paper_only"] is True
    assert result["real_action_blocked"] is True


