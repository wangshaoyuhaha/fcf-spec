import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.batch_analysis import run_paper_analysis_batch, summarize_batch_results
from btc_finance_platform.batch_error_collector import collect_batch_input_errors
from btc_finance_platform.batch_manifest import build_batch_manifest
from btc_finance_platform.batch_quality import evaluate_batch_quality, assert_batch_quality_gate


def make_batch_and_summary():
    batch = run_paper_analysis_batch([
        {"symbol": "BTCUSDT", "price": 65000, "reference_price": 64000},
        {"symbol": "ETHUSDT", "price": 3500, "reference_price": 3600},
    ])
    summary = summarize_batch_results(batch)
    return batch, summary


def test_collect_batch_input_errors_all_valid():
    result = collect_batch_input_errors([
        {"symbol": "BTCUSDT", "price": 65000, "reference_price": 64000},
        {"symbol": "ETHUSDT", "price": 3500, "reference_price": 3600},
    ])

    assert result["ok"] is True
    assert result["total_count"] == 2
    assert result["valid_count"] == 2
    assert result["error_count"] == 0
    assert result["paper_only"] is True
    assert result["real_order"] is False


def test_collect_batch_input_errors_with_bad_item():
    result = collect_batch_input_errors([
        {"symbol": "BTCUSDT", "price": 65000, "reference_price": 64000},
        {"symbol": "ETHUSDT", "price": 0, "reference_price": 3600},
    ])

    assert result["ok"] is True
    assert result["total_count"] == 2
    assert result["valid_count"] == 1
    assert result["error_count"] == 1
    assert "price must be positive" in result["errors"][0]["error"]


def test_batch_quality_gate():
    batch, summary = make_batch_and_summary()
    quality = evaluate_batch_quality(batch, summary)

    assert quality["ok"] is True
    assert quality["paper_only"] is True
    assert quality["action"] == "NO_LIVE_ACTION"
    assert quality["quality_status"] == "REVIEW_REQUIRED"
    assert assert_batch_quality_gate(quality) is True


def test_batch_quality_detects_high_risk():
    batch = run_paper_analysis_batch([
        {"symbol": "BTCUSDT", "price": 70000, "reference_price": 64000},
        {"symbol": "ETHUSDT", "price": 3500, "reference_price": 3600},
    ])
    summary = summarize_batch_results(batch)
    quality = evaluate_batch_quality(batch, summary)

    assert quality["high_risk_count"] >= 1
    assert quality["quality_note"] == "HIGH_RISK_PRESENT"
    assert quality["real_execution"] is False


def test_batch_manifest():
    batch, summary = make_batch_and_summary()
    quality = evaluate_batch_quality(batch, summary)
    manifest = build_batch_manifest(batch, summary, quality)

    assert manifest["ok"] is True
    assert manifest["type"] == "paper_batch_manifest"
    assert manifest["count"] == 2
    assert manifest["paper_only"] is True
    assert manifest["real_money_impact"] is False
    assert manifest["operator_review_required"] is True


def test_batch_manifest_rejects_non_paper_quality():
    batch, summary = make_batch_and_summary()
    quality = evaluate_batch_quality(batch, summary)
    quality["paper_only"] = False

    try:
        build_batch_manifest(batch, summary, quality)
    except AssertionError as exc:
        assert "paper-only quality" in str(exc)
    else:
        raise AssertionError("expected AssertionError")
