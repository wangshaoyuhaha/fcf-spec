import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
 sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_evidence_closeout import build_p36_evidence_completion_gate
from btc_finance_platform.paper_governance_evidence_closeout import build_p36_evidence_final_packet
from btc_finance_platform.paper_governance_evidence_closeout import build_p36_governance_evidence_closeout


if __name__ == "__main__":
 result = {
  "governance_evidence_closeout": build_p36_governance_evidence_closeout(),
  "evidence_final_packet": build_p36_evidence_final_packet(),
  "evidence_completion_gate": build_p36_evidence_completion_gate(),
 }
 print(json.dumps(result, indent=2, sort_keys=True))
