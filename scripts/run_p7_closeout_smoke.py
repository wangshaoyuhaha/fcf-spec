import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_operator_console_closeout import build_p7_closeout_package
from btc_finance_platform.paper_operator_console_closeout import get_p7_operator_console_capabilities
from btc_finance_platform.paper_operator_console_closeout import get_p7_safety_acceptance
from btc_finance_platform.paper_operator_console_closeout import get_p7_to_p8_transition_anchor

if __name__ == "__main__":
    root = Path(ROOT)
    fixture = root / "fixtures" / "sample_multi_market_batch.json"
    actions = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
    result = {
        "capabilities": get_p7_operator_console_capabilities(),
        "safety": get_p7_safety_acceptance(),
        "transition": get_p7_to_p8_transition_anchor(),
        "closeout": build_p7_closeout_package(fixture, actions),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
