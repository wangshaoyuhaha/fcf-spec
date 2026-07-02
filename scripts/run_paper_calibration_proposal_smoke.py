import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_calibration_proposal import (
    build_calibration_proposal_contract,
    build_calibration_ui_contract,
    build_risk_bucket_performance_index,
)

if __name__ == "__main__":
    root = Path(ROOT)
    fixture = root / "fixtures" / "sample_multi_market_batch.json"
    actions = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
    outcomes = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}

    performance = build_risk_bucket_performance_index(fixture, actions, outcomes)
    proposal = build_calibration_proposal_contract(fixture, actions, outcomes)
    ui = build_calibration_ui_contract(fixture, actions, outcomes)

    print(json.dumps({
        "performance_ok": performance["ok"],
        "bucket_count": performance["bucket_count"],
        "proposal_ok": proposal["ok"],
        "proposal_count": proposal["proposal_count"],
        "ui_ok": ui["ok"],
        "validation_ok": ui["validation"]["ok"],
        "training_status": ui["training_status"],
        "calibration_status": ui["calibration_status"],
    }, indent=2, sort_keys=True))
