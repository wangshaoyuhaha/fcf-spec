import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_backtest_baseline import (
    build_calibration_seed_baseline,
    build_paper_backtest_baseline,
    build_paper_backtest_input_contract,
)

if __name__ == "__main__":
    root = Path(ROOT)
    fixture = root / "fixtures" / "sample_multi_market_batch.json"
    actions = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
    outcomes = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}

    contract = build_paper_backtest_input_contract(fixture, actions, outcomes)
    backtest = build_paper_backtest_baseline(fixture, actions, outcomes)
    seed = build_calibration_seed_baseline(fixture, actions, outcomes)

    print(json.dumps({
        "contract_ok": contract["ok"],
        "contract_count": contract["count"],
        "backtest_ok": backtest["ok"],
        "usable_count": backtest["usable_count"],
        "average_outcome_score": backtest["average_outcome_score"],
        "seed_ok": seed["ok"],
        "training_status": seed["training_status"],
        "calibration_status": seed["calibration_status"],
    }, indent=2, sort_keys=True))
