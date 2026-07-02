import os
import sys
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.local_data_loader import build_local_data_manifest
from btc_finance_platform.local_data_loader import load_paper_batch_from_file
from btc_finance_platform.local_data_loader import load_paper_csv
from btc_finance_platform.local_data_loader import load_paper_json
from btc_finance_platform.local_data_loader import load_paper_records
from btc_finance_platform.local_data_loader import normalize_paper_record


JSON_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.json"
CSV_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.csv"


def test_normalize_paper_record_uppercases_symbol_and_numbers():
    result = normalize_paper_record({
        "symbol": "btcusdt",
        "price": "65000",
        "reference_price": "64000",
    })

    assert result == {
        "symbol": "BTCUSDT",
        "price": 65000.0,
        "reference_price": 64000.0,
    }


def test_load_paper_json_fixture():
    records = load_paper_json(JSON_FIXTURE)

    assert len(records) == 3
    assert records[0]["symbol"] == "BTCUSDT"
    assert records[1]["symbol"] == "ETHUSDT"
    assert records[2]["symbol"] == "SOLUSDT"


def test_load_paper_csv_fixture():
    records = load_paper_csv(CSV_FIXTURE)

    assert len(records) == 3
    assert records[0]["symbol"] == "BTCUSDT"
    assert records[0]["price"] == 65000.0
    assert records[0]["reference_price"] == 64000.0


def test_load_paper_batch_from_json_file():
    result = load_paper_batch_from_file(JSON_FIXTURE)

    assert result["ok"] is True
    assert result["type"] == "local_paper_batch_load"
    assert result["format"] == "json"
    assert result["count"] == 3
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_order"] is False
    assert result["operator_review_required"] is True


def test_load_paper_batch_from_csv_file():
    result = load_paper_batch_from_file(CSV_FIXTURE)

    assert result["ok"] is True
    assert result["format"] == "csv"
    assert result["count"] == 3
    assert "BTCUSDT" in result["symbols"]
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False


def test_build_local_data_manifest_for_json_and_csv():
    result = build_local_data_manifest([JSON_FIXTURE, CSV_FIXTURE])

    assert result["ok"] is True
    assert result["type"] == "local_data_manifest"
    assert result["source_count"] == 2
    assert result["total_records"] == 6
    assert result["paper_only"] is True
    assert result["real_api_key_required"] is False
    assert result["real_balance"] is False
    assert result["real_position"] is False
    assert len(result["sources"][0]["sha256"]) == 64


def test_loader_rejects_unsupported_extension(tmp_path):
    bad_file = tmp_path / "sample.txt"
    bad_file.write_text("symbol,price,reference_price", encoding="utf-8")

    with pytest.raises(ValueError, match="unsupported local paper data file type"):
        load_paper_records(bad_file)
