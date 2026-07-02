import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.batch_analysis import run_paper_analysis_batch, summarize_batch_results
from btc_finance_platform.batch_input import validate_paper_input_batch
from btc_finance_platform.batch_report import render_batch_report


def test_validate_paper_input_batch():
    batch = validate_paper_input_batch([
        {"symbol": "btcusdt", "price": 65000, "reference_price": 64000},
        {"symbol": "ethusdt", "price": 3500, "reference_price": 3600},
    ])

    assert batch["ok"] is True
    assert batch["count"] == 2
    assert batch["paper_only"] is True
    assert batch["real_order"] is False
    assert batch["items"][0]["symbol"] == "BTCUSDT"


def test_run_paper_analysis_batch():
    batch = run_paper_analysis_batch([
        {"symbol": "BTCUSDT", "price": 65000, "reference_price": 64000},
        {"symbol": "ETHUSDT", "price": 3500, "reference_price": 3600},
    ])

    assert batch["ok"] is True
    assert batch["count"] == 2
    assert batch["paper_only"] is True
    assert batch["real_execution"] is False
    assert batch["results"][0]["analysis"]["symbol"] == "BTCUSDT"


def test_summarize_batch_results():
    batch = run_paper_analysis_batch([
        {"symbol": "BTCUSDT", "price": 70000, "reference_price": 64000},
        {"symbol": "ETHUSDT", "price": 3500, "reference_price": 3600},
    ])
    summary = summarize_batch_results(batch)

    assert summary["ok"] is True
    assert summary["count"] == 2
    assert "BTCUSDT" in summary["symbols"]
    assert summary["paper_only"] is True
    assert summary["real_money_impact"] is False


def test_render_batch_report():
    batch = run_paper_analysis_batch([
        {"symbol": "BTCUSDT", "price": 65000, "reference_price": 64000},
        {"symbol": "ETHUSDT", "price": 3500, "reference_price": 3600},
    ])
    summary = summarize_batch_results(batch)
    report = render_batch_report(batch, summary)

    assert "PAPER_ONLY_BATCH_REVIEW_REQUIRED" in report
    assert "NO_LIVE_ACTION" in report
    assert "BTCUSDT" in report
    assert "ETHUSDT" in report
    assert "no real exchange API" in report


def test_batch_rejects_empty_payloads():
    try:
        validate_paper_input_batch([])
    except ValueError as exc:
        assert "must not be empty" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_batch_rejects_bad_item():
    try:
        run_paper_analysis_batch([
            {"symbol": "BTCUSDT", "price": 0, "reference_price": 64000},
        ])
    except ValueError as exc:
        assert "price must be positive" in str(exc)
    else:
        raise AssertionError("expected ValueError")
