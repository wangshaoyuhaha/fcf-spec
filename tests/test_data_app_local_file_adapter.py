import os
import sys
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from data_app.local_file_adapter import build_local_file_adapter_contract
from data_app.local_file_adapter import build_local_file_adapter_result
from data_app.local_file_adapter import load_a_share_rows_from_csv
from data_app.local_file_adapter import load_a_share_rows_from_json
from data_app.local_file_adapter import load_a_share_rows_from_local_file
from data_app.local_file_adapter import normalize_a_share_file_row


CSV_FIXTURE = Path(ROOT) / "data_app" / "fixtures" / "a_share_sample.csv"
JSON_FIXTURE = Path(ROOT) / "data_app" / "fixtures" / "a_share_sample.json"


def test_local_file_adapter_contract_is_read_only():
    result = build_local_file_adapter_contract()

    assert result["app"] == "DATA-APP"
    assert result["active_input_types"] == ["csv", "json"]
    assert result["reserved_input_types"] == ["excel"]
    assert result["excel_enabled"] is False
    assert result["paper_only"] is True
    assert result["local_only"] is True
    assert result["read_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["api_key_required"] is False
    assert result["real_order_allowed"] is False
    assert result["real_execution_allowed"] is False
    assert result["real_money_impact_allowed"] is False


def test_load_a_share_rows_from_csv_fixture():
    rows = load_a_share_rows_from_csv(CSV_FIXTURE)

    assert len(rows) == 2
    assert rows[0]["symbol"] == "000001.SZ"
    assert rows[0]["open"] == 10.0
    assert rows[0]["is_st"] is False


def test_load_a_share_rows_from_json_fixture():
    rows = load_a_share_rows_from_json(JSON_FIXTURE)

    assert len(rows) == 2
    assert rows[1]["symbol"] == "000002.SZ"
    assert rows[1]["close"] == 20.5
    assert rows[1]["listing_days"] == 1500


def test_build_local_file_adapter_result_accepts_valid_csv():
    result = build_local_file_adapter_result(CSV_FIXTURE)

    assert result["ok"] is True
    assert result["source_type"] == "csv"
    assert result["row_count"] == 2
    assert result["accepted_count"] == 2
    assert result["rejected_count"] == 0
    assert result["operator_review_required"] is True


def test_local_file_adapter_rejects_missing_required_field(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("date,symbol,name\n2026-07-05,000001.SZ,SAMPLE\n", encoding="utf-8")

    result = build_local_file_adapter_result(bad)

    assert result["ok"] is False
    assert result["accepted_count"] == 0
    assert result["rejected_count"] == 1


def test_local_file_adapter_rejects_unsupported_extension(tmp_path):
    bad = tmp_path / "bad.txt"
    bad.write_text("not supported", encoding="utf-8")

    with pytest.raises(ValueError, match="unsupported local file type"):
        load_a_share_rows_from_local_file(bad)


def test_normalize_a_share_file_row_converts_numbers_and_flags():
    result = normalize_a_share_file_row({
        "symbol": "000001.sz",
        "open": "10.0",
        "listing_days": "1000",
        "is_st": "false",
    })

    assert result["symbol"] == "000001.SZ"
    assert result["open"] == 10.0
    assert result["listing_days"] == 1000
    assert result["is_st"] is False
