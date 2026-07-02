import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_model_registry import build_model_registry_baseline

if __name__ == "__main__":
    root = Path(ROOT)
    fixture = root / "fixtures" / "sample_multi_market_batch.json"
    actions = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
    outcomes = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}

    registry = build_model_registry_baseline(fixture, actions, outcomes)

    print(json.dumps({
        "ok": registry["ok"],
        "type": registry["type"],
        "registry_version": registry["registry_version"],
        "validation_ok": registry["validation"]["ok"],
        "training_status": registry["training_status"],
        "calibration_status": registry["calibration_status"],
        "deployment_status": registry["deployment_status"],
        "parameter_update_allowed_now": registry["parameter_update_allowed_now"],
    }, indent=2, sort_keys=True))
