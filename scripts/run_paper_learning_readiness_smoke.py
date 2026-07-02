import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_learning_readiness import build_calibration_readiness_gate
from btc_finance_platform.paper_learning_readiness import build_learning_dataset_quality_gate
from btc_finance_platform.paper_learning_readiness import build_learning_readiness_bundle

if __name__ == "__main__":
    root = Path(ROOT)
    fixture = root / "fixtures" / "sample_multi_market_batch.json"
    actions = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
    outcomes = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}
    quality = build_learning_dataset_quality_gate(fixture, actions, outcomes)
    calibration = build_calibration_readiness_gate(fixture, actions, outcomes)
    bundle = build_learning_readiness_bundle(fixture, actions, outcomes)
    print(json.dumps({
        "quality_gate": quality["gate"],
        "calibration_gate": calibration["gate"],
        "bundle_ok": bundle["ok"],
        "next_phase": bundle["next_phase"],
        "training_status": bundle["training_status"],
    }, indent=2, sort_keys=True))
