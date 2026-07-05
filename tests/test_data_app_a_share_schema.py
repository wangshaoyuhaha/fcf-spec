import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from data_app.a_share_schema import OPTIONAL_ENRICHMENT_FIELDS
from data_app.a_share_schema import REQUIRED_A_SHARE_FIELDS
from data_app.a_share_schema import build_a_share_schema_contract
from data_app.a_share_schema import validate_a_share_required_fields
from data_app.a_share_schema import validate_a_share_schema_row


def _sample_row():
    return {
        "date": "2026-07-05",
        "symbol": "000001.SZ",
        "name": "SAMPLE",
        "open": 10.0,
        "high": 10.5,
        "low": 9.8,
        "close": 10.2,
        "prev_close": 10.0,
        "volume": 1000000,
        "amount": 10200000,
        "turnover_rate": 2.5,
        "float_market_cap": 1000000000,
        "total_market_cap": 1200000000,
        "listing_days": 1000,
        "is_st": False,
        "limit_up_price": 11.0,
        "limit_down_price": 9.0,
        "sector_code": "BK_SAMPLE",
        "sector_name": "Sample Sector",
        "trading_status": "trading",
    }


def test_a_share_schema_contract_has_required_fields():
    result = build_a_share_schema_contract()

    assert result["app"] == "DATA-APP"
    assert result["market"] == "A_SHARE"
    assert result["schema_version"] == "a_share_daily_v1"
    assert "symbol" in result["required_fields"]
    assert "turnover_rate" in result["required_fields"]
    assert "sector_code" in result["required_fields"]
    assert "dragon_tiger_list" in result["optional_enrichment_fields"]


def test_a_share_schema_contract_preserves_safety_boundary():
    result = build_a_share_schema_contract()

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


def test_validate_a_share_schema_row_passes_for_complete_row():
    result = validate_a_share_schema_row(_sample_row())

    assert result["ok"] is True
    assert result["market"] == "A_SHARE"
    assert result["required"]["ok"] is True
    assert result["numeric"]["ok"] is True
    assert result["operator_review_required"] is True


def test_validate_a_share_schema_row_fails_for_missing_required_field():
    row = _sample_row()
    row.pop("turnover_rate")

    result = validate_a_share_required_fields(row)

    assert result["ok"] is False
    assert result["missing_required_fields"] == ["turnover_rate"]


def test_validate_a_share_schema_row_fails_for_invalid_numeric_field():
    row = _sample_row()
    row["amount"] = "bad-number"

    result = validate_a_share_schema_row(row)

    assert result["ok"] is False
    assert result["numeric"]["invalid_numeric_fields"] == ["amount"]


def test_required_and_optional_fields_are_separated():
    assert "date" in REQUIRED_A_SHARE_FIELDS
    assert "symbol" in REQUIRED_A_SHARE_FIELDS
    assert "announcement_summary" in OPTIONAL_ENRICHMENT_FIELDS
    assert "announcement_summary" not in REQUIRED_A_SHARE_FIELDS
