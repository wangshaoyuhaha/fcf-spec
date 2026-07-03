import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p13_ai_learning_memory_ledger import append_learning_memory_event


if __name__ == "__main__":
    ledger = Path(ROOT) / "runtime" / "operator_console" / "ai_learning_memory_ledger.json"

    result = append_learning_memory_event(
        ledger,
        "validation_observed",
        "P13 learning boundary validation observed in local-only paper mode",
        {
            "pytest_expected": 464,
            "paper_only": True,
            "operator_review_required": True,
        },
    )

    if result["event_count"] < 1:
        raise SystemExit("learning ledger should contain at least one event")

    if result["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    if result["patch_auto_apply_allowed"] is not False:
        raise SystemExit("patch auto apply must remain false")

    print(json.dumps(result, indent=2, sort_keys=True))
