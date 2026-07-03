import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_feature_source_audit import write_feature_source_audit_report


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "learning_engine" / "feature_source_audit_report.json"

    rows = [
        {
            "feature_id": "twitter_sentiment_index",
            "source_type": "sentiment",
            "regime": "range_chop",
            "correlation": 0.04,
            "observation_count": 120,
        },
        {
            "feature_id": "volume_breakout_score",
            "source_type": "market_feature",
            "regime": "trend_up",
            "correlation": 0.36,
            "observation_count": 90,
        },
        {
            "feature_id": "macro_uncertainty_note",
            "source_type": "macro_text",
            "regime": "liquidity_stress",
            "correlation": -0.22,
            "observation_count": 15,
        },
    ]

    result = write_feature_source_audit_report(rows, output)
    report = result["report"]

    if report["audit_status"] != "READY_FOR_OPERATOR_REVIEW":
        raise SystemExit("feature audit must wait for operator review")

    if report["audit_policy"]["auto_prune_allowed"] is not False:
        raise SystemExit("auto prune must remain false")

    if report["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    print(json.dumps(result, indent=2, sort_keys=True))
