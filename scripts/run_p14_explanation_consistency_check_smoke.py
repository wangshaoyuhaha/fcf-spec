import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_explanation_consistency_check import write_explanation_consistency_report


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "learning_engine" / "explanation_consistency_report.json"

    source_report = {
        "type": "p14_data_quality_sentry_report",
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "real_order": False,
        "real_execution": False,
    }

    explanation = "This is a paper-only local audit report. Operator review is required."
    claims = {
        "paper_only": True,
        "local_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "real_order": False,
        "real_execution": False,
    }

    result = write_explanation_consistency_report(source_report, explanation, claims, output)
    report = result["report"]

    if report["consistency_policy"]["ai_explanation_override_allowed"] is not False:
        raise SystemExit("AI explanation override must remain false")

    if report["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    if report["operator_review_required"] is not True:
        raise SystemExit("operator review must remain required")

    print(json.dumps(result, indent=2, sort_keys=True))
