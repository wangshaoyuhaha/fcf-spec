import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_learning_audit import (
    build_feedback_to_calibration_handoff,
    build_learning_event_audit_trail,
    build_learning_memory_markdown_report,
)

if __name__ == "__main__":
    root = Path(ROOT)
    fixture = root / "fixtures" / "sample_multi_market_batch.json"
    actions = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
    outcomes = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}

    audit = build_learning_event_audit_trail(fixture, actions, outcomes)
    handoff = build_feedback_to_calibration_handoff(fixture, actions, outcomes)
    report = build_learning_memory_markdown_report(fixture, actions, outcomes)

    print(json.dumps({
        "audit_ok": audit["ok"],
        "audit_event_count": audit["event_count"],
        "handoff_ok": handoff["ok"],
        "handoff_count": handoff["count"],
        "report_ok": report["ok"],
        "training_status": handoff["training_status"],
    }, indent=2, sort_keys=True))
