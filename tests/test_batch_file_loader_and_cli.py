import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.batch_cli import build_parser, main, run_batch_cli
from btc_finance_platform.batch_file_loader import (
    load_paper_batch_file,
    load_paper_batch_from_csv,
    load_paper_batch_from_json,
)


def test_load_paper_batch_from_json_list():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "batch.json"
        path.write_text(json.dumps([
            {"symbol": "BTCUSDT", "price": 65000, "reference_price": 64000}
        ]), encoding="utf-8")

        payloads = load_paper_batch_from_json(str(path))

        assert len(payloads) == 1
        assert payloads[0]["symbol"] == "BTCUSDT"


def test_load_paper_batch_from_json_items_dict():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "batch.json"
        path.write_text(json.dumps({
            "items": [
                {"symbol": "ETHUSDT", "price": 3500, "reference_price": 3600}
            ]
        }), encoding="utf-8")

        payloads = load_paper_batch_file(str(path))

        assert len(payloads) == 1
        assert payloads[0]["symbol"] == "ETHUSDT"


def test_load_paper_batch_from_csv():
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "batch.csv"
        path.write_text(
            "symbol,price,reference_price\nBTCUSDT,65000,64000\n",
            encoding="utf-8",
        )

        payloads = load_paper_batch_from_csv(str(path))

        assert len(payloads) == 1
        assert payloads[0]["price"] == 65000.0
        assert payloads[0]["reference_price"] == 64000.0


def test_load_paper_batch_file_rejects_missing_file():
    try:
        load_paper_batch_file("missing_file.json")
    except FileNotFoundError:
        assert True
    else:
        raise AssertionError("expected FileNotFoundError")


def test_batch_cli_runs_without_export(capsys):
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = Path(temp_dir) / "batch.json"
        input_path.write_text(json.dumps([
            {"symbol": "BTCUSDT", "price": 65000, "reference_price": 64000},
            {"symbol": "ETHUSDT", "price": 3500, "reference_price": 3600},
        ]), encoding="utf-8")

        exit_code = main(["--input", str(input_path)])
        captured = capsys.readouterr()

        assert exit_code == 0
        assert '"type": "paper_batch_cli_result"' in captured.out
        assert '"paper_only": true' in captured.out
        assert '"real_order": false' in captured.out


def test_batch_cli_runs_with_export():
    parser = build_parser()

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = Path(temp_dir) / "batch.json"
        output_path = Path(temp_dir) / "batch_report.md"

        input_path.write_text(json.dumps([
            {"symbol": "BTCUSDT", "price": 65000, "reference_price": 64000},
            {"symbol": "ETHUSDT", "price": 3500, "reference_price": 3600},
        ]), encoding="utf-8")

        args = parser.parse_args(["--input", str(input_path), "--output", str(output_path)])
        result = run_batch_cli(args)

        assert result["ok"] is True
        assert result["paper_only"] is True
        assert result["real_execution"] is False
        assert result["export"]["ok"] is True
        assert output_path.exists()
        assert "NO_LIVE_ACTION" in output_path.read_text(encoding="utf-8")


def test_batch_cli_rejects_bad_item():
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = Path(temp_dir) / "batch.json"
        input_path.write_text(json.dumps([
            {"symbol": "BTCUSDT", "price": 0, "reference_price": 64000}
        ]), encoding="utf-8")

        try:
            main(["--input", str(input_path)])
        except ValueError as exc:
            assert "price must be positive" in str(exc)
        else:
            raise AssertionError("expected ValueError")
