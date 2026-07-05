import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from stock_app.contracts.limit_up_potential import HIGH_POTENTIAL
from stock_app.contracts.limit_up_potential import REJECTED_LEVEL
from stock_app.contracts.limit_up_potential import WATCH_ONLY_LEVEL
from stock_app.contracts.ranked_watchlist import build_candidate_report
from stock_app.contracts.ranked_watchlist import build_ranked_watchlist
from stock_app.contracts.ranked_watchlist import write_candidate_report


def base_record():
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


def sample_records():
    high = base_record()
    watch = base_record()
    watch["symbol"] = "000001"
    watch["name"] = "Sample Watch"
    watch["data_quality_state"] = "PASS_LIMITED"
    rejected = base_record()
    rejected["symbol"] = "300000"
    rejected["name"] = "Sample Reject"
    rejected["trading_status"] = "SUSPENDED"
    return [watch, rejected, high]


def test_build_ranked_watchlist_orders_high_before_watch_only():
    result = build_ranked_watchlist(sample_records(), trade_date="2026-07-05", source_manifest_id="m1")
    assert result["app"] == "STOCK-APP"
    assert result["contract_version"] == "STOCK_APP_RANKED_WATCHLIST_V1"
    assert result["input_count"] == 3
    assert result["candidate_count"] == 2
    assert result["excluded_count"] == 1
    assert result["ranked_watchlist"][0]["potential_level"] == HIGH_POTENTIAL
    assert result["ranked_watchlist"][1]["potential_level"] == WATCH_ONLY_LEVEL
    assert result["excluded"][0]["potential_level"] == REJECTED_LEVEL


def test_ranked_watchlist_rows_have_required_fields():
    result = build_ranked_watchlist(sample_records())
    row = result["ranked_watchlist"][0]
    assert "score_breakdown" in row
    assert "reason_codes" in row
    assert "risk_flags" in row
    assert "data_quality_state" in row
    assert "confidence_level" in row
    assert "data_sources" in row
    assert row["operator_review_required"] is True
    assert row["real_action_blocked"] is True


def test_candidate_report_contains_operator_review_and_ai_handoff():
    result = build_candidate_report(sample_records(), trade_date="2026-07-05", source_manifest_id="m1")
    assert result["contract_version"] == "STOCK_APP_CANDIDATE_REPORT_V1"
    assert result["summary"]["input_count"] == 3
    assert result["summary"]["candidate_count"] == 2
    assert result["operator_review_packet"]["operator_review_required"] is True
    assert result["operator_review_packet"]["ai_can_explain_only"] is True
    assert result["operator_review_packet"]["ai_can_modify_score"] is False
    assert result["handoff_to_ai_context"]["allowed"] is True
    assert result["handoff_to_ai_context"]["score_modification_allowed"] is False


def test_candidate_report_blocks_trade_and_guarantee_claims():
    result = build_candidate_report(sample_records())
    assert result["buy_instruction_allowed"] is False
    assert result["sell_instruction_allowed"] is False
    assert result["guaranteed_limit_up_claim_allowed"] is False
    assert result["real_action_blocked"] is True


def test_write_candidate_report_creates_json_artifact(tmp_path):
    output = tmp_path / "candidate_report.json"
    result = write_candidate_report(sample_records(), output, trade_date="2026-07-05", source_manifest_id="m1")
    assert result["ok"] is True
    assert output.exists()
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["contract_version"] == "STOCK_APP_CANDIDATE_REPORT_V1"
    assert saved["summary"]["candidate_count"] == 2
    assert saved["paper_only"] is True
