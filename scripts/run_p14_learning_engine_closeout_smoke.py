import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_learning_engine_closeout import default_p14_closeout_modules
from btc_finance_platform.p14_learning_engine_closeout import write_learning_engine_closeout_report


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "learning_engine" / "p14_learning_engine_closeout_report.json"

    result = write_learning_engine_closeout_report(
        default_p14_closeout_modules(),
        output,
    )

    report = result["report"]

    if report["closeout_status"] != "READY_FOR_OPERATOR_REVIEW":
        raise SystemExit("P14 closeout must be ready for operator review")

    if report["closeout_policy"]["merge_to_main_allowed_now"] is not False:
        raise SystemExit("merge to main must remain false")

    if report["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    print(json.dumps(result, indent=2, sort_keys=True))
