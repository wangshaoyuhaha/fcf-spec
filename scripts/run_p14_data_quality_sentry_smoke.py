import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_data_quality_sentry import write_data_quality_sentry_report


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "learning_engine" / "data_quality_sentry_report.json"

    sources = [
        {
            "source_id": "paper_price_feed",
            "source_type": "market_feature",
            "missing_ratio": 0.0,
            "latency_seconds": 30,
            "outlier_ratio": 0.0,
        },
        {
            "source_id": "paper_sentiment_feed",
            "source_type": "sentiment",
            "missing_ratio": 0.08,
            "latency_seconds": 20,
            "outlier_ratio": 0.01,
        },
    ]

    result = write_data_quality_sentry_report(sources, output)
    report = result["report"]

    if report["quality_policy"]["auto_quarantine_allowed"] is not False:
        raise SystemExit("auto quarantine must remain false")

    if report["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    if report["operator_review_required"] is not True:
        raise SystemExit("operator review must remain required")

    print(json.dumps(result, indent=2, sort_keys=True))
