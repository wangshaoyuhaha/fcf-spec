import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p13_operator_console_snapshot import write_operator_console_status_snapshot


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "operator_console" / "index.html"
    snapshot = Path(ROOT) / "runtime" / "operator_console" / "status_snapshot.json"

    result = write_operator_console_status_snapshot(output, snapshot)

    if result["snapshot"]["operator_console_ready"] is not True:
        raise SystemExit("operator console snapshot should be ready")

    if result["snapshot"]["trading_buttons_enabled"] is not False:
        raise SystemExit("trading buttons must remain disabled")

    if result["snapshot"]["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    if result["snapshot"]["operator_review_required"] is not True:
        raise SystemExit("operator review must remain required")

    print(json.dumps(result, indent=2, sort_keys=True))
