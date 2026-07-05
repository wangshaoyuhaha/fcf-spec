import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from stock_app.contracts.sector_theme_linkage import MEDIUM_LINKAGE
from stock_app.contracts.sector_theme_linkage import NO_LINKAGE
from stock_app.contracts.sector_theme_linkage import STRONG_LINKAGE
from stock_app.contracts.sector_theme_linkage import build_sector_theme_linkage_package
from stock_app.contracts.sector_theme_linkage import evaluate_sector_theme_linkage


def strong_record():
    return {
        "symbol": "600000",
        "name": "Sample Strong",
        "sector_code": "BK001",
        "sector_name": "AI Computing",
        "theme_tags": ["AI", "Computing"],
        "sector_strength_score": 88,
        "theme_heat_score": 82,
        "market_breadth_score": 76,
        "data_quality_state": "PASS_STRICT",
    }


def test_pass_strict_strong_sector_theme_gets_high_confidence():
    result = evaluate_sector_theme_linkage(strong_record())
    assert result["sector_theme_level"] == STRONG_LINKAGE
    assert result["confidence_level"] == "HIGH"
    assert "SECTOR_ACTIVE" in result["reason_codes"]
    assert "THEME_HEAT_DETECTED" in result["reason_codes"]
    assert "THEME_LINKAGE_CONFIRMED" in result["reason_codes"]
    assert result["real_action_blocked"] is True


def test_pass_limited_discounts_score_and_adds_risk_flag():
    record = strong_record()
    record["data_quality_state"] = "PASS_LIMITED"
    result = evaluate_sector_theme_linkage(record)
    assert result["sector_theme_level"] == MEDIUM_LINKAGE
    assert "DATA_QUALITY_LIMITED" in result["risk_flags"]
    assert result["operator_review_required"] is True


def test_fail_quarantine_blocks_linkage_scoring():
    record = strong_record()
    record["data_quality_state"] = "FAIL_QUARANTINE"
    result = evaluate_sector_theme_linkage(record)
    assert result["sector_theme_score"] == 0.0
    assert result["sector_theme_level"] == NO_LINKAGE
    assert "DATA_QUALITY_QUARANTINE" in result["risk_flags"]


def test_missing_sector_and_theme_adds_risk_flags():
    record = strong_record()
    record["sector_code"] = ""
    record["sector_name"] = ""
    record["theme_tags"] = []
    record["sector_strength_score"] = 5
    record["theme_heat_score"] = 5
    record["market_breadth_score"] = 5
    result = evaluate_sector_theme_linkage(record)
    assert result["sector_theme_level"] == NO_LINKAGE
    assert "MISSING_SECTOR_INFO" in result["risk_flags"]
    assert "MISSING_THEME_TAGS" in result["risk_flags"]
    assert "PUBLIC_SIGNAL_WEAK" in result["risk_flags"]


def test_string_theme_tags_are_normalized():
    record = strong_record()
    record["theme_tags"] = "AI, computing, robot"
    result = evaluate_sector_theme_linkage(record)
    assert result["theme_tags"] == ["AI", "computing", "robot"]


def test_scores_are_clamped_to_safe_range():
    record = strong_record()
    record["sector_strength_score"] = 200
    record["theme_heat_score"] = -20
    record["market_breadth_score"] = 100
    result = evaluate_sector_theme_linkage(record)
    assert result["sector_strength_score"] == 100.0
    assert result["theme_heat_score"] == 0.0
    assert result["market_breadth_score"] == 100.0


def test_build_sector_theme_linkage_package_counts_levels():
    strong = strong_record()
    medium = strong_record()
    medium["symbol"] = "000001"
    medium["sector_strength_score"] = 60
    medium["theme_heat_score"] = 55
    medium["market_breadth_score"] = 50
    weak = strong_record()
    weak["symbol"] = "300000"
    weak["sector_strength_score"] = 30
    weak["theme_heat_score"] = 25
    weak["market_breadth_score"] = 20

    result = build_sector_theme_linkage_package([strong, medium, weak])
    assert result["app"] == "STOCK-APP"
    assert result["contract_version"] == "STOCK_APP_SECTOR_THEME_V1"
    assert result["input_count"] == 3
    assert result["strong_linkage_count"] == 1
    assert result["medium_linkage_count"] == 1
    assert result["weak_linkage_count"] == 1
    assert result["paper_only"] is True
    assert result["real_action_blocked"] is True
