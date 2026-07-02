import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_learning_ui import build_learning_dataset_index
from btc_finance_platform.paper_learning_ui import build_learning_memory_ui_contract
from btc_finance_platform.paper_learning_ui import build_learning_memory_ui_manifest
from btc_finance_platform.paper_learning_ui import write_learning_memory_ui_bundle

if __name__ == "__main__":
    root = Path(ROOT)
    fixture = root / "fixtures" / "sample_multi_market_batch.json"
    output_dir = root / "artifacts" / "learning_memory_ui_bundle"
    actions = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
    outcomes = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}
    contract = build_learning_memory_ui_contract(fixture, actions, outcomes)
    index = build_learning_dataset_index(fixture, actions, outcomes)
    manifest = build_learning_memory_ui_manifest(fixture, actions, outcomes)
    written = write_learning_memory_ui_bundle(fixture, output_dir, actions, outcomes)
    print(json.dumps({
        "contract": {
            "ok": contract["ok"],
            "type": contract["type"],
            "count": contract["count"],
            "validation": contract["validation"],
        },
        "index": {
            "ok": index["ok"],
            "type": index["type"],
            "count": index["count"],
        },
        "manifest": {
            "ok": manifest["ok"],
            "type": manifest["type"],
            "manifest_version": manifest["manifest_version"],
            "validation": manifest["validation"],
        },
        "written": {
            "ok": written["ok"],
            "type": written["type"],
            "output_dir": written["output_dir"],
            "manifest_file": written["manifest_file"],
        },
    }, indent=2, sort_keys=True))
