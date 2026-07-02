import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_operator_console import build_operator_console_contract
from btc_finance_platform.paper_operator_console import write_operator_console_bundle

if __name__ == "__main__":
    root = Path(ROOT)
    fixture = root / "fixtures" / "sample_multi_market_batch.json"
    output_dir = root / "artifacts" / "operator_console_bundle"
    contract = build_operator_console_contract(fixture)
    written = write_operator_console_bundle(fixture, output_dir)
    print(json.dumps({
        "contract": {
            "ok": contract["ok"],
            "type": contract["type"],
            "contract_version": contract["contract_version"],
            "dashboard_count": contract["dashboard"]["count"],
            "queue_count": contract["review_queue"]["count"],
            "validation": contract["validation"],
            "paper_only": contract["paper_only"],
            "operator_review_required": contract["operator_review_required"],
        },
        "written": {
            "ok": written["ok"],
            "type": written["type"],
            "output_dir": written["output_dir"],
            "contract_file": written["contract_file"],
        },
    }, indent=2, sort_keys=True))
