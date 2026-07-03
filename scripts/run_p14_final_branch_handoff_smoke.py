import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_final_branch_handoff import default_final_branch_handoff_items
from btc_finance_platform.p14_final_branch_handoff import write_final_branch_handoff_checkpoint


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "learning_engine" / "p14_final_branch_handoff_checkpoint.json"

    result = write_final_branch_handoff_checkpoint(
        branch_name="p13-operator-console",
        target_branch="main",
        latest_commit_label="add P14 final archive manifest",
        validation_passed_count=598,
        handoff_items=default_final_branch_handoff_items(),
        path=output,
    )

    checkpoint = result["checkpoint"]

    if checkpoint["handoff_status"] != "READY_FOR_OPERATOR_BRANCH_HANDOFF":
        raise SystemExit("branch handoff must be ready only for operator review")

    if checkpoint["handoff_policy"]["merge_to_main_allowed_now"] is not False:
        raise SystemExit("merge to main must remain false")

    if checkpoint["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    print(json.dumps(result, indent=2, sort_keys=True))
