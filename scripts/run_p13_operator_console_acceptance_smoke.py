import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p13_operator_console_acceptance import write_operator_console_acceptance_summary


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "operator_console" / "index.html"
    summary_path = Path(ROOT) / "runtime" / "operator_console" / "acceptance_summary.json"

    result = write_operator_console_acceptance_summary(output, summary_path)
    summary = result["summary"]

    if summary["acceptance_status"] != "ACCEPTED_FOR_READ_ONLY_PAPER_CONSOLE":
        raise SystemExit("operator console acceptance status is invalid")

    if summary["p13_scope_closed"] is not True:
        raise SystemExit("P13 scope should be closed in acceptance summary")

    if summary["safe_to_execute_real_money"] is not False:
        raise SystemExit("real money execution must remain false")

    if summary["operator_review_required"] is not True:
        raise SystemExit("operator review must remain required")

    print(json.dumps(result, indent=2, sort_keys=True))
