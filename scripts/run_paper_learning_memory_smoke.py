import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_learning_memory import build_operator_feedback_dataset
from btc_finance_platform.paper_learning_memory import build_paper_outcome_tracking_contract
from btc_finance_platform.paper_learning_memory import write_learning_memory_bundle

if __name__ == "__main__":
    root = Path(ROOT)
    fixture = root / "fixtures" / "sample_multi_market_batch.json"
    output_dir = root / "artifacts" / "learning_memory_bundle"
    actions = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
    outcomes = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}
    dataset = build_operator_feedback_dataset(fixture, actions, outcomes)
    tracking = build_paper_outcome_tracking_contract(fixture, actions, outcomes)
    written = write_learning_memory_bundle(fixture, output_dir, actions, outcomes)
    print(json.dumps({
        "dataset": {
            "ok": dataset["ok"],
            "type": dataset["type"],
            "count": dataset["count"],
            "action_counts": dataset["action_counts"],
            "outcome_counts": dataset["outcome_counts"],
            "validation": dataset["validation"],
        },
        "tracking": {
            "ok": tracking["ok"],
            "type": tracking["type"],
            "count": tracking["count"],
            "outcome_counts": tracking["outcome_counts"],
        },
        "written": {
            "ok": written["ok"],
            "type": written["type"],
            "output_dir": written["output_dir"],
            "schema_file": written["schema_file"],
            "dataset_file": written["dataset_file"],
            "tracking_file": written["tracking_file"],
        },
    }, indent=2, sort_keys=True))
