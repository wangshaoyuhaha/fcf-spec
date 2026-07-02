import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_audit import build_governance_audit_trail
from btc_finance_platform.paper_governance_audit import write_governance_audit_trail


if __name__ == "__main__":
    root = Path(ROOT)
    sources = [
        root / "fixtures" / "sample_paper_batch.json",
        root / "fixtures" / "sample_paper_batch.csv",
    ]
    output = root / "artifacts" / "governance_audit_trail.json"

    trail = build_governance_audit_trail(sources, operator_status="pending")
    written = write_governance_audit_trail(sources, output, operator_status="pending")

    print(json.dumps({
        "trail": trail,
        "written": {
            "ok": written["ok"],
            "type": written["type"],
            "output_file": written["output_file"],
            "paper_only": written["paper_only"],
            "operator_review_required": written["operator_review_required"],
        },
    }, indent=2, sort_keys=True))
