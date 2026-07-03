import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_alpha_decay_profiling import write_alpha_decay_report


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "learning_engine" / "alpha_decay_report.json"

    rows = [
        {
            "source_id": "twitter_sentiment_index",
            "source_type": "sentiment",
            "window_scores": {"1h": 0.18, "4h": 0.31, "24h": 0.08},
        },
        {
            "source_id": "macro_uncertainty_note",
            "source_type": "macro_text",
            "window_scores": {"24h": 0.12, "72h": 0.28, "168h": 0.22},
        },
        {
            "source_id": "volume_breakout_score",
            "source_type": "market_feature",
            "window_scores": {"4h": 0.16, "24h": 0.33, "72h": 0.19},
        },
    ]

    result = write_alpha_decay_report(rows, output)
    report = result["report"]

    if report["report_status"] != "READY_FOR_OPERATOR_REVIEW":
        raise SystemExit("alpha decay report must wait for operator review")

    if report["audit_policy"]["auto_weight_update_allowed"] is not False:
        raise SystemExit("auto weight update must remain false")

    if report["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    print(json.dumps(result, indent=2, sort_keys=True))
