import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_operator_workflow import build_cli_to_ui_artifact_export_bridge
from btc_finance_platform.paper_operator_workflow import build_operator_workflow_state
from btc_finance_platform.paper_operator_workflow import write_operator_workflow_bundle

if __name__ == "__main__":
    root = Path(ROOT)
    fixture = root / "fixtures" / "sample_multi_market_batch.json"
    output_dir = root / "artifacts" / "operator_workflow_bundle"
    actions = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
    state = build_operator_workflow_state(fixture, actions)
    bridge = build_cli_to_ui_artifact_export_bridge(fixture, actions)
    written = write_operator_workflow_bundle(fixture, output_dir, actions)
    print(json.dumps({
        "state": {
            "ok": state["ok"],
            "type": state["type"],
            "count": state["count"],
            "action_counts": state["action_counts"],
            "paper_only": state["paper_only"],
        },
        "bridge": {
            "ok": bridge["ok"],
            "type": bridge["type"],
            "bridge_version": bridge["bridge_version"],
            "workflow_validation": bridge["workflow_validation"],
        },
        "written": {
            "ok": written["ok"],
            "type": written["type"],
            "output_dir": written["output_dir"],
            "bridge_file": written["bridge_file"],
        },
    }, indent=2, sort_keys=True))
