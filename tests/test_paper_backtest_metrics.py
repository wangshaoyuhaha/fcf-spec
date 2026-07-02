import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_backtest_metrics import (
    build_backtest_metric_summary,
    build_calibration_evaluation_baseline,
    build_backtest_readable_report,
    write_backtest_metrics_report_bundle,
)

MULTI_MARKET_FIXTURE = Path(ROOT) / "fixtures" / "sample_multi_market_batch.json"
ACTIONS = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
OUTCOMES = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}


def test_backtest_metric_summary_counts_outcomes():
    result = build_backtest_metric_summary(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "backtest_metric_summary"
    assert result["count"] == 3
    assert result["usable_count"] == 2
    assert result["success_count"] == 1
    assert result["failure_count"] == 1


def test_backtest_metric_summary_rates():
    result = build_backtest_metric_summary(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["success_rate"] == 0.5
    assert result["failure_rate"] == 0.5
    assert result["average_outcome_score"] == 0.0


def test_calibration_evaluation_baseline_builds_buckets():
    result = build_calibration_evaluation_baseline(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "calibration_evaluation_baseline"
    assert result["bucket_count"] >= 1
    assert result["training_status"] == "not_trained"
    assert result["calibration_status"] == "not_calibrated"


def test_calibration_evaluation_does_not_update_parameters():
    result = build_calibration_evaluation_baseline(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["decision"] == "calibration_evaluation_paper_only_no_parameter_update"
    assert all(bucket["real_world_actions_allowed"] is False for bucket in result["buckets"])


def test_backtest_readable_report_contains_notices():
    result = build_backtest_readable_report(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "backtest_readable_report"
    assert "# Paper Backtest And Calibration Evaluation Report" in result["markdown"]
    assert "This report does not train a model." in result["markdown"]


def test_backtest_metrics_report_bundle_writes_files(tmp_path):
    output_dir = tmp_path / "backtest_metrics_bundle"
    result = write_backtest_metrics_report_bundle(MULTI_MARKET_FIXTURE, output_dir, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert Path(result["metrics_file"]).exists()
    assert Path(result["evaluation_file"]).exists()
    assert Path(result["report_file"]).exists()


def test_backtest_metrics_report_bundle_preserves_safety(tmp_path):
    output_dir = tmp_path / "backtest_metrics_bundle_safety"
    result = write_backtest_metrics_report_bundle(MULTI_MARKET_FIXTURE, output_dir, ACTIONS, OUTCOMES)
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True
