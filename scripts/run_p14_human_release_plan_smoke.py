import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_human_release_plan import default_human_release_plan_items
from btc_finance_platform.p14_human_release_plan import write_human_release_plan_packet


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "learning_engine" / "p14_human_release_plan_packet.json"

    result = write_human_release_plan_packet(
        target_branch="main",
        tag_name="v14-learning-engine-paper",
        validation_passed_count=614,
        release_items=default_human_release_plan_items(),
        path=output,
    )

    packet = result["packet"]

    if packet["plan_status"] != "READY_FOR_HUMAN_RELEASE_REVIEW":
        raise SystemExit("human release plan must be ready only for human review")

    if packet["release_plan_policy"]["auto_release_allowed"] is not False:
        raise SystemExit("auto release must remain false")

    if packet["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    print(json.dumps(result, indent=2, sort_keys=True))
