import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from data_app.health_check import FAIL_QUARANTINE
from data_app.health_check import PASS_LIMITED
from data_app.health_check import PASS_STRICT
from data_app.health_check import build_data_app_health_check
from data_app.health_check import route_by_health_check_state


CSV_FIXTURE = Path(ROOT) / "data_app" / "fixtures" / "a_share_sample.csv"


def test_health_check_passes_strict_for_clean_fixture():
    result = build_data_app_health_check(CSV_FIXTURE)

    assert result["state"] == PASS_STRICT
    assert result["row_count"] == 2
    assert result["accepted_count"] == 2
    assert result["rejected_count"] == 0
    assert all(result["hard_checks"].values())
    assert "DATA_OK" in result["reason_codes"]


def test_health_check_preserves_safety_boundary():
    result = build_data_app_health_check(CSV_FIXTURE)

    assert result["paper_only"] is True
    assert result["local_only"] is True
    assert result["read_only"] is True
    assert result["operator_review_required"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["api_key_required"] is False
    assert result["real_order_allowed"] is False
    assert result["real_execution_allowed"] is False
    assert result["real_money_impact_allowed"] is False


def test_health_route_pass_strict_goes_to_clean_universe():
    health = build_data_app_health_check(CSV_FIXTURE)
    result = route_by_health_check_state(health)

    assert result["state"] == PASS_STRICT
    assert result["destination"] == "CLEAN_UNIVERSE"
    assert result["ranking_allowed"] is True
    assert result["operator_review_required"] is True


def test_health_route_pass_limited_goes_to_watchlist_only():
    result = route_by_health_check_state({"state": PASS_LIMITED})

    assert result["destination"] == "WATCHLIST_ONLY"
    assert result["ranking_allowed"] is False
    assert result["real_order_allowed"] is False


def test_health_route_fail_quarantine_goes_to_quarantine():
    result = route_by_health_check_state({"state": FAIL_QUARANTINE})

    assert result["destination"] == "QUARANTINE"
    assert result["ranking_allowed"] is False
    assert result["real_execution_allowed"] is False


def test_health_check_fails_quarantine_for_missing_fields(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("date,symbol,name\n2026-07-05,000001.SZ,SAMPLE\n", encoding="utf-8")

    result = build_data_app_health_check(bad)

    assert result["state"] == FAIL_QUARANTINE
    assert "REQUIRED_FIELDS_FAILED" in result["reason_codes"]


def test_health_check_fails_quarantine_for_bad_price_sanity(tmp_path):
    bad = tmp_path / "bad_price.csv"
    bad.write_text(
        "date,symbol,name,open,high,low,close,prev_close,volume,amount,turnover_rate,float_market_cap,total_market_cap,listing_days,is_st,limit_up_price,limit_down_price,sector_code,sector_name,trading_status\n"
        "2026-07-05,000001.SZ,SAMPLE,10,9,11,10,10,100,1000,1,1000,1000,100,false,11,9,BK,Sector,trading\n",
        encoding="utf-8",
    )

    result = build_data_app_health_check(bad)

    assert result["state"] == FAIL_QUARANTINE
    assert "PRICE_SANITY_FAILED" in result["reason_codes"]
