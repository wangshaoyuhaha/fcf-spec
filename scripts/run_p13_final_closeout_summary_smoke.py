import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p13_final_closeout_summary import write_p13_final_closeout_summary


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "operator_console" / "index.html"
    ledger = Path(ROOT) / "runtime" / "operator_console" / "ai_learning_memory_ledger.json"
    summary_path = Path(ROOT) / "runtime" / "operator_console" / "p13_final_closeout_summary.json"

    result = write_p13_final_closeout_summary(output, ledger, summary_path)
    summary = result["summary"]

    if summary["p13_final_status"] != "READY_FOR_MANUAL_MAIN_MERGE_REVIEW":
        raise SystemExit("P13 final status is invalid")

    if summary["merge_to_main_completed"] is not False:
        raise SystemExit("merge must not be marked completed")

    if summary["release_created"] is not False:
        raise SystemExit("release must not be marked created")

    if summary["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    print(json.dumps(result, indent=2, sort_keys=True))
