import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_human_merge_plan import default_human_merge_plan_items
from btc_finance_platform.p14_human_merge_plan import write_human_merge_plan_packet


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "learning_engine" / "p14_human_merge_plan_packet.json"

    result = write_human_merge_plan_packet(
        source_branch="p13-operator-console",
        target_branch="main",
        validation_passed_count=606,
        plan_items=default_human_merge_plan_items(),
        path=output,
    )

    packet = result["packet"]

    if packet["plan_status"] != "READY_FOR_HUMAN_MERGE_REVIEW":
        raise SystemExit("human merge plan must be ready only for human review")

    if packet["merge_plan_policy"]["auto_execute_allowed"] is not False:
        raise SystemExit("auto execute must remain false")

    if packet["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    print(json.dumps(result, indent=2, sort_keys=True))
