import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.data_schema import (
    validate_paper_batch_schema,
    validate_paper_input_schema,
)


def test_validate_paper_input_schema():
    result = validate_paper_input_schema({
        "symbol": "btcusdt",
        "price": 65000,
        "reference_price": 64000,
    })

    assert result["ok"] is True
    assert result["symbol"] == "BTCUSDT"
    assert result["paper_only"] is True
    assert result["real_order"] is False


def test_validate_paper_batch_schema():
    result = validate_paper_batch_schema([
        {"symbol": "BTCUSDT", "price": 65000, "reference_price": 64000},
        {"symbol": "ETHUSDT", "price": 3500, "reference_price": 3600},
    ])

    assert result["ok"] is True
    assert result["count"] == 2
    assert "BTCUSDT" in result["symbols"]
    assert result["paper_only"] is True
    assert result["real_execution"] is False


def test_schema_fixture_file_validates():
    fixture = Path(ROOT) / "fixtures" / "sample_paper_batch.json"
    payloads = json.loads(fixture.read_text(encoding="utf-8-sig"))

    result = validate_paper_batch_schema(payloads)

    assert result["ok"] is True
    assert result["count"] == 3
    assert "SOLUSDT" in result["symbols"]


def test_schema_rejects_missing_field():
    try:
        validate_paper_input_schema({"symbol": "BTCUSDT", "price": 65000})
    except ValueError as exc:
        assert "missing required fields" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_schema_rejects_bad_price():
    try:
        validate_paper_input_schema({"symbol": "BTCUSDT", "price": 0, "reference_price": 64000})
    except ValueError as exc:
        assert "price must be positive" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_batch_schema_rejects_empty_list():
    try:
        validate_paper_batch_schema([])
    except ValueError as exc:
        assert "must not be empty" in str(exc)
    else:
        raise AssertionError("expected ValueError")

