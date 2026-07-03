import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_final_completion_receipt import default_final_completion_items
from btc_finance_platform.p14_final_completion_receipt import write_final_completion_receipt


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "learning_engine" / "p14_final_completion_receipt.json"

    result = write_final_completion_receipt(
        branch_name="p13-operator-console",
        validation_passed_count=622,
        completion_items=default_final_completion_items(),
        path=output,
    )

    receipt = result["receipt"]

    if receipt["completion_status"] != "P14_COMPLETE_READY_FOR_HUMAN_CONTROLLED_NEXT_STEP":
        raise SystemExit("P14 completion receipt must be complete only for human-controlled next step")

    if receipt["completion_policy"]["auto_release_allowed"] is not False:
        raise SystemExit("auto release must remain false")

    if receipt["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    print(json.dumps(result, indent=2, sort_keys=True))
