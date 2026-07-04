import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_next_phase_evidence import build_p32_evidence_audit_trail
from btc_finance_platform.paper_next_phase_evidence import build_p32_evidence_gate
from btc_finance_platform.paper_next_phase_evidence import build_p32_evidence_index


if __name__ == "__main__":
    result = {
        "evidence_index": build_p32_evidence_index(),
        "evidence_audit_trail": build_p32_evidence_audit_trail(),
        "evidence_gate": build_p32_evidence_gate(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
