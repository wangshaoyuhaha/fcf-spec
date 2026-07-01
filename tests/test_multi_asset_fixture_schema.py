import json
from pathlib import Path

from fcf.api.dify_http_adapter import ROUTE_BATCH, route_dify_http_request
from fcf.pipelines.market_input_pipeline import process_raw_market_batch
from fcf.schemas.raw_market_input_schema import normalize_raw_market_input


FIXTURE_PATH = Path("fixtures/raw_market_data_multi_asset.json")


def _fixture_rows():
    with FIXTURE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_multi_asset_fixture_file_exists_and_loads():
    rows = _fixture_rows()

    assert FIXTURE_PATH.exists()
    assert len(rows) == 4
    assert [row["asset_class"] for row in rows] == [
        "crypto",
        "equities",
        "fx",
        "commodities",
    ]


def test_multi_asset_fixture_rows_pass_schema_normalization():
    rows = _fixture_rows()
    normalized_rows = [normalize_raw_market_input(row) for row in rows]

    assert [row["asset_class"] for row in normalized_rows] == [
        "crypto",
        "equities",
        "fx",
        "commodities",
    ]
    assert [row["symbol"] for row in normalized_rows] == [
        "BTCUSDT",
        "AAPL",
        "EURUSD",
        "XAUUSD",
    ]
    assert [row["market_type"] for row in normalized_rows] == [
        "perpetual",
        "spot",
        "spot",
        "futures",
    ]
    assert all(row["last_price"] > 0 for row in normalized_rows)


def test_market_input_pipeline_processes_multi_asset_fixture_batch():
    result = process_raw_market_batch(
        rows=_fixture_rows(),
        correlation_id="p4-d9-multi-asset-pipeline",
    )

    assert result["status"] == "completed"
    assert result["pipeline"] == "market_input_pipeline"
    assert result["schema"] == "raw_market_input_schema"
    assert result["event_count"] == 4
    assert result["symbols"] == ["BTCUSDT", "AAPL", "EURUSD", "XAUUSD"]
    assert result["asset_classes"] == ["crypto", "equities", "fx", "commodities"]
    assert result["market_types"] == ["perpetual", "spot", "spot", "futures"]
    assert result["replay"]["status"] == "completed"
    assert result["replay"]["event_count"] == 4


def test_dify_batch_adapter_processes_multi_asset_fixture_batch():
    response = route_dify_http_request(
        "POST",
        ROUTE_BATCH,
        {
            "correlation_id": "p4-d9-multi-asset-dify-batch",
            "rows": _fixture_rows(),
        },
    )

    assert response["http_status"] == 200
    assert response["body"]["ok"] is True

    data = response["body"]["data"]

    assert data["event_count"] == 4
    assert data["symbols"] == ["BTCUSDT", "AAPL", "EURUSD", "XAUUSD"]
    assert data["asset_classes"] == ["crypto", "equities", "fx", "commodities"]
    assert data["market_types"] == ["perpetual", "spot", "spot", "futures"]
    assert data["replay"]["event_count"] == 4
