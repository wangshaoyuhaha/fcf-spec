import json
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
)

if __name__ == "__main__":
    root = Path(ROOT)
    fixture = root / "fixtures" / "sample_multi_market_batch.json"
    actions = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
    outcomes = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}

    metrics = build_backtest_metric_summary(fixture, actions, outcomes)
    evaluation = build_calibration_evaluation_baseline(fixture, actions, outcomes)
    report = build_backtest_readable_report(fixture, actions, outcomes)

    print(json.dumps({
        "metrics_ok": metrics["ok"],
        "usable_count": metrics["usable_count"],
        "success_rate": metrics["success_rate"],
        "evaluation_ok": evaluation["ok"],
        "bucket_count": evaluation["bucket_count"],
        "report_ok": report["ok"],
        "training_status": report["training_status"],
        "calibration_status": report["calibration_status"],
    }, indent=2, sort_keys=True))
