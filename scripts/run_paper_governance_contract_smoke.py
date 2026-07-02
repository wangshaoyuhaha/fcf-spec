import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_contract import build_governance_decision_index
from btc_finance_platform.paper_governance_contract import build_governance_ui_contract
from btc_finance_platform.paper_governance_contract import write_governance_contract_bundle


if __name__ == "__main__":
    root = Path(ROOT)
    sources = [
        root / "fixtures" / "sample_paper_batch.json",
        root / "fixtures" / "sample_paper_batch.csv",
    ]
    output_dir = root / "artifacts" / "paper_governance_contract"

    contract = build_governance_ui_contract(sources, operator_status="pending")
    index = build_governance_decision_index(sources, operator_status="pending")
    bundle = write_governance_contract_bundle(sources, output_dir, operator_status="pending")

    print(json.dumps({
        "contract": {
            "ok": contract["ok"],
            "type": contract["type"],
            "count": contract["count"],
            "status_counts": contract["status_counts"],
            "validation": contract["validation"],
            "paper_only": contract["paper_only"],
            "operator_review_required": contract["operator_review_required"],
        },
        "index": index,
        "bundle": {
            "ok": bundle["ok"],
            "type": bundle["type"],
            "output_dir": bundle["output_dir"],
            "contract_file": bundle["contract_file"],
            "index_file": bundle["index_file"],
            "markdown_file": bundle["markdown_file"],
        },
    }, indent=2, sort_keys=True))
