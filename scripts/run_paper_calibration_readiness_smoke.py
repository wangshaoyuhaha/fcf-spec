import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_calibration_readiness import (
    build_backtest_ui_readiness_gate,
    build_calibration_acceptance_gate,
    build_p9_readiness_bundle,
)

if __name__ == "__main__":
    root = Path(ROOT)
    fixture = root / "fixtures" / "sample_multi_market_batch.json"
    actions = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
    outcomes = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}

    acceptance = build_calibration_acceptance_gate(fixture, actions, outcomes)
    ui = build_backtest_ui_readiness_gate(fixture, actions, outcomes)
    bundle = build_p9_readiness_bundle(fixture, actions, outcomes)

    print(json.dumps({
        "acceptance_gate": acceptance["gate"],
        "ui_gate": ui["gate"],
        "bundle_ok": bundle["ok"],
        "training_status": bundle["training_status"],
        "calibration_status": bundle["calibration_status"],
        "parameter_update_allowed_now": bundle["parameter_update_allowed_now"],
    }, indent=2, sort_keys=True))
