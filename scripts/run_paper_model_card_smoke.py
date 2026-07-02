import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_model_card import (
    build_model_registry_readable_report,
    build_operator_model_approval_gate,
    build_paper_model_card,
)

if __name__ == "__main__":
    root = Path(ROOT)
    fixture = root / "fixtures" / "sample_multi_market_batch.json"
    actions = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
    outcomes = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}

    card = build_paper_model_card(fixture, actions, outcomes)
    gate = build_operator_model_approval_gate(fixture, actions, outcomes)
    report = build_model_registry_readable_report(fixture, actions, outcomes)

    print(json.dumps({
        "card_ok": card["ok"],
        "gate": gate["gate"],
        "report_ok": report["ok"],
        "training_status": report["training_status"],
        "deployment_status": report["deployment_status"],
        "real_world_actions_allowed": report["real_world_actions_allowed"],
    }, indent=2, sort_keys=True))
