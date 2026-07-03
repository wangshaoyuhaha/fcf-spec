import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p13_operator_console import build_operator_console_state
from btc_finance_platform.p13_operator_console import write_operator_console_html

if __name__ == "__main__":
    state = build_operator_console_state(
        {
            "project_name": "BTC finance platform",
            "current_stage": "P13-D1-D3",
            "paper_only": True,
            "operator_review_required": True,
            "ui_mode": "read_only",
            "local_only": True,
        },
        {"all_checks_passed": True, "pytest_passed": True, "pytest_count": 433},
        {"release_published": True, "release_tag": "v12-paper-final-archive"},
    )
    result = write_operator_console_html(state, Path(ROOT) / "runtime" / "operator_console" / "index.html")
    if state["operator_console_ready"] is not True:
        raise SystemExit("operator console should be ready")
    if result["trading_buttons_enabled"] is not False:
        raise SystemExit("trading buttons must remain disabled")
    print(json.dumps({"state": state, "html": result}, indent=2, sort_keys=True))
