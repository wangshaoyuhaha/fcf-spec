import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from data_app.health_check import FAIL_QUARANTINE
from data_app.health_check import PASS_LIMITED
from data_app.health_check import PASS_STRICT
from data_app.universe import build_data_app_universe_contract
from data_app.universe import build_data_app_universe_package
from data_app.universe import write_data_app_universe_package


CSV_FIXTURE = Path(ROOT) / "data_app" / "fixtures" / "a_share_sample.csv"

HEADER = "date,symbol,name,open,high,low,close,prev_close,volume,amount,turnover_rate,float_market_cap,total_market_cap,listing_days,is_st,limit_up_price,limit_down_price,sector_code,sector_name,trading_status\n"


def test_universe_contract_preserves_safety_boundary():
    result = build_data_app_universe_contract()

    assert result["app"] == "DATA-APP"
    assert result["market"] == "A_SHARE"
    assert PASS_STRICT in result["allowed_states"]
    assert PASS_LIMITED in result["allowed_states"]
    assert FAIL_QUARANTINE in result["allowed_states"]
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


def test_pass_strict_fixture_enters_clean_universe():
    result = build_data_app_universe_package(CSV_FIXTURE)

    assert result["data_quality_state"] == PASS_STRICT
    assert result["destination"] == "CLEAN_UNIVERSE"
    assert result["ranking_allowed"] is True
    assert result["clean_universe_count"] == 2
    assert result["watchlist_only_count"] == 0
    assert result["quarantine_count"] == 0


def test_pass_limited_data_enters_watchlist_only(tmp_path):
    sample = tmp_path / "limited.csv"
    sample.write_text(
        HEADER
        + "2026-07-05,000001.SZ,SAMPLE,10,10.5,9.8,10.2,10,1000,10000,1,1000,1000,100,false,11,9,BK,Sector,suspended\n",
        encoding="utf-8",
    )

    result = build_data_app_universe_package(sample)

    assert result["data_quality_state"] == PASS_LIMITED
    assert result["destination"] == "WATCHLIST_ONLY"
    assert result["ranking_allowed"] is False
    assert result["clean_universe_count"] == 0
    assert result["watchlist_only_count"] == 1
    assert result["quarantine_count"] == 0


def test_missing_required_fields_enter_quarantine(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("date,symbol,name\n2026-07-05,000001.SZ,SAMPLE\n", encoding="utf-8")

    result = build_data_app_universe_package(bad)

    assert result["data_quality_state"] == FAIL_QUARANTINE
    assert result["destination"] == "QUARANTINE"
    assert result["ranking_allowed"] is False
    assert result["clean_universe_count"] == 0
    assert result["quarantine_count"] == 1


def test_bad_price_sanity_enters_quarantine(tmp_path):
    bad = tmp_path / "bad_price.csv"
    bad.write_text(
        HEADER
        + "2026-07-05,000001.SZ,SAMPLE,10,9,11,10,10,1000,10000,1,1000,1000,100,false,11,9,BK,Sector,trading\n",
        encoding="utf-8",
    )

    result = build_data_app_universe_package(bad)

    assert result["data_quality_state"] == FAIL_QUARANTINE
    assert result["quarantine_count"] == 1
    assert "PRICE_SANITY_FAILED" in result["health_check"]["reason_codes"]


def test_write_data_app_universe_package(tmp_path):
    output = tmp_path / "universe" / "package.json"
    result = write_data_app_universe_package(CSV_FIXTURE, output)

    assert result["ok"] is True
    assert output.exists()

    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["contract_version"] == "DATA_APP_UNIVERSE_D6"
    assert saved["data_quality_state"] == PASS_STRICT


def test_universe_package_keeps_operator_review_and_blocks_real_actions():
    result = build_data_app_universe_package(CSV_FIXTURE)

    assert result["operator_review_required"] is True
    assert result["paper_only"] is True
    assert result["local_only"] is True
    assert result["read_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["api_key_required"] is False
    assert result["real_order_allowed"] is False
    assert result["real_execution_allowed"] is False
    assert result["real_money_impact_allowed"] is False
