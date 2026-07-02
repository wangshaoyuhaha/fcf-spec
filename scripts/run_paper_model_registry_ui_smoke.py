import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_model_registry_ui import (
    build_model_registry_ui_contract,
    build_model_registry_ui_manifest,
    build_model_version_index,
)

if __name__ == "__main__":
    root = Path(ROOT)
    fixture = root / "fixtures" / "sample_multi_market_batch.json"
    actions = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
    outcomes = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}

    index = build_model_version_index(fixture, actions, outcomes)
    ui = build_model_registry_ui_contract(fixture, actions, outcomes)
    manifest = build_model_registry_ui_manifest(fixture, actions, outcomes)

    print(json.dumps({
        "index_ok": index["ok"],
        "model_count": index["count"],
        "ui_ok": ui["ok"],
        "validation_ok": ui["validation"]["ok"],
        "manifest_ok": manifest["ok"],
        "card_count": manifest["card_count"],
        "deployment_status": manifest["deployment_status"],
        "real_world_actions_allowed": manifest["real_world_actions_allowed"],
    }, indent=2, sort_keys=True))
