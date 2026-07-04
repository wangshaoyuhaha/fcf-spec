import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_phase_transition_evidence import build_p33_evidence_gate
from btc_finance_platform.paper_phase_transition_evidence import build_p33_transition_evidence_audit
from btc_finance_platform.paper_phase_transition_evidence import build_p33_transition_evidence_index


if __name__ == "__main__":
    result = {
        "transition_evidence_index": build_p33_transition_evidence_index(),
        "transition_evidence_audit": build_p33_transition_evidence_audit(),
        "evidence_gate": build_p33_evidence_gate(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
