import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_operator_console_acceptance import build_operator_console_acceptance_summary
from btc_finance_platform.paper_operator_console_acceptance import build_operator_console_ui_acceptance_gate
from btc_finance_platform.paper_operator_console_acceptance import write_operator_console_acceptance_bundle

if __name__ == "__main__":
    root = Path(ROOT)
    fixture = root / "fixtures" / "sample_multi_market_batch.json"
    output_dir = root / "artifacts" / "operator_console_acceptance_bundle"
    actions = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
    gate = build_operator_console_ui_acceptance_gate(fixture, actions)
    summary = build_operator_console_acceptance_summary(fixture, actions)
    bundle = write_operator_console_acceptance_bundle(fixture, output_dir, actions)
    print(json.dumps({
        "gate": gate,
        "summary": summary,
        "bundle": {
            "ok": bundle["ok"],
            "type": bundle["type"],
            "output_dir": bundle["output_dir"],
            "registry_file": bundle["registry_file"],
            "gate_file": bundle["gate_file"],
            "summary_file": bundle["summary_file"],
            "report_file": bundle["report_file"],
        },
    }, indent=2, sort_keys=True))
