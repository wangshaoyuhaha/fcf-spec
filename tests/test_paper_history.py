import os
import sys
import tempfile
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.analysis_flow import run_paper_analysis_flow
from btc_finance_platform.paper_history import save_paper_run_record, summarize_paper_history


def test_save_paper_run_record():
    result = run_paper_analysis_flow({"symbol": "BTCUSDT", "price": 65000, "reference_price": 64000})

    with tempfile.TemporaryDirectory() as temp_dir:
        saved = save_paper_run_record(result["record"], temp_dir)

        assert saved["ok"] is True
        assert saved["paper_only"] is True
        assert saved["real_order"] is False
        assert Path(saved["path"]).exists()


def test_summarize_paper_history():
    result = run_paper_analysis_flow({"symbol": "BTCUSDT", "price": 65000, "reference_price": 64000})

    with tempfile.TemporaryDirectory() as temp_dir:
        save_paper_run_record(result["record"], temp_dir)
        summary = summarize_paper_history(temp_dir)

        assert summary["ok"] is True
        assert summary["run_count"] == 1
        assert summary["paper_only"] is True
        assert summary["real_execution"] is False


def test_save_paper_run_record_rejects_non_paper():
    result = run_paper_analysis_flow({"symbol": "BTCUSDT", "price": 65000, "reference_price": 64000})
    record = dict(result["record"])
    record["paper_only"] = False

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            save_paper_run_record(record, temp_dir)
        except AssertionError as exc:
            assert "paper-only" in str(exc)
        else:
            raise AssertionError("expected AssertionError")


def test_save_paper_run_record_rejects_real_order():
    result = run_paper_analysis_flow({"symbol": "BTCUSDT", "price": 65000, "reference_price": 64000})
    record = dict(result["record"])
    record["real_order"] = True

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            save_paper_run_record(record, temp_dir)
        except AssertionError as exc:
            assert "real order" in str(exc)
        else:
            raise AssertionError("expected AssertionError")


def test_summarize_empty_history():
    with tempfile.TemporaryDirectory() as temp_dir:
        summary = summarize_paper_history(temp_dir)

        assert summary["ok"] is True
        assert summary["run_count"] == 0
        assert summary["files"] == []
        assert summary["paper_only"] is True
