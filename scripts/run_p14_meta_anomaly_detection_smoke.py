import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_meta_anomaly_detection import write_meta_anomaly_report


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "learning_engine" / "meta_anomaly_report.json"

    windows = [
        {
            "window_id": "last_30_days_high_confidence",
            "regime": "trend_up",
            "average_confidence": 0.91,
            "actual_win_rate": 0.35,
            "max_paper_drawdown_pct": 0.12,
        },
        {
            "window_id": "last_30_days_drawdown",
            "regime": "liquidity_stress",
            "average_confidence": 0.62,
            "actual_win_rate": 0.50,
            "max_paper_drawdown_pct": 0.34,
        },
    ]

    result = write_meta_anomaly_report(windows, output)
    report = result["report"]

    if report["report_status"] != "READY_FOR_OPERATOR_REVIEW":
        raise SystemExit("meta anomaly report must wait for operator review")

    if report["meta_policy"]["auto_mode_switch_allowed"] is not False:
        raise SystemExit("auto mode switch must remain false")

    if report["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    print(json.dumps(result, indent=2, sort_keys=True))
