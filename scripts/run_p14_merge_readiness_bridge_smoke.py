import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_merge_readiness_bridge import default_merge_readiness_items
from btc_finance_platform.p14_merge_readiness_bridge import write_merge_readiness_bridge


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "learning_engine" / "p14_merge_readiness_bridge.json"

    result = write_merge_readiness_bridge(
        source_branch="p13-operator-console",
        target_branch="main",
        readiness_items=default_merge_readiness_items(),
        path=output,
    )

    report = result["report"]

    if report["readiness_status"] != "READY_FOR_OPERATOR_MERGE_REVIEW":
        raise SystemExit("merge bridge must be ready only for operator merge review")

    if report["merge_policy"]["merge_to_main_allowed_now"] is not False:
        raise SystemExit("merge to main must remain false")

    if report["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    print(json.dumps(result, indent=2, sort_keys=True))
