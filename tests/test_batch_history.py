import os
import sys
import tempfile
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.batch_analysis import run_paper_analysis_batch, summarize_batch_results
from btc_finance_platform.batch_history import create_batch_run_record, save_batch_run_record, summarize_batch_history
from btc_finance_platform.batch_report import render_batch_report


def make_record():
    batch = run_paper_analysis_batch([
        {"symbol": "BTCUSDT", "price": 65000, "reference_price": 64000},
        {"symbol": "ETHUSDT", "price": 3500, "reference_price": 3600},
    ])
    summary = summarize_batch_results(batch)
    report = render_batch_report(batch, summary)
    return create_batch_run_record(batch, summary, report)


def test_create_batch_run_record():
    record = make_record()
    assert record["ok"] is True
    assert record["type"] == "paper_batch_run_record"
    assert record["count"] == 2
    assert record["paper_only"] is True
    assert record["real_order"] is False


def test_save_batch_run_record():
    record = make_record()
    with tempfile.TemporaryDirectory() as temp_dir:
        saved = save_batch_run_record(record, temp_dir)
        assert saved["ok"] is True
        assert saved["paper_only"] is True
        assert Path(saved["path"]).exists()


def test_summarize_batch_history():
    record = make_record()
    with tempfile.TemporaryDirectory() as temp_dir:
        save_batch_run_record(record, temp_dir)
        summary = summarize_batch_history(temp_dir)
        assert summary["ok"] is True
        assert summary["batch_run_count"] == 1
        assert summary["paper_only"] is True
        assert summary["real_execution"] is False


def test_save_batch_record_rejects_non_paper():
    record = make_record()
    record["paper_only"] = False
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            save_batch_run_record(record, temp_dir)
        except AssertionError as exc:
            assert "paper-only" in str(exc)
        else:
            raise AssertionError("expected AssertionError")


def test_summarize_empty_batch_history():
    with tempfile.TemporaryDirectory() as temp_dir:
        summary = summarize_batch_history(temp_dir)
        assert summary["ok"] is True
        assert summary["batch_run_count"] == 0
        assert summary["files"] == []
