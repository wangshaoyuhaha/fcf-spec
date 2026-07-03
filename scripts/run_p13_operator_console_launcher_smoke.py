import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p13_operator_console_launcher import build_operator_console_launch_plan

if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "operator_console" / "index.html"
    result = build_operator_console_launch_plan(output)
    if result["operator_console_ready"] is not True:
        raise SystemExit("operator console launcher should be ready")
    if result["trading_buttons_enabled"] is not False:
        raise SystemExit("trading buttons must remain disabled")
    if result["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")
    print(json.dumps(result, indent=2, sort_keys=True))
