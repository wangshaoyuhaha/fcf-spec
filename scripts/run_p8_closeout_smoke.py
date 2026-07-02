import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_learning_closeout import build_p8_closeout_package

if __name__ == "__main__":
    root = Path(ROOT)
    fixture = root / "fixtures" / "sample_multi_market_batch.json"
    actions = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
    outcomes = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}
    package = build_p8_closeout_package(fixture, actions, outcomes)
    print(json.dumps({
        "ok": package["ok"],
        "type": package["type"],
        "phase": package["phase"],
        "status": package["status"],
        "next_phase": package["next_phase"],
        "training_status": package["training_status"],
    }, indent=2, sort_keys=True))
