import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
 sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_transition_closeout import build_p34_governance_transition_closeout
from btc_finance_platform.paper_governance_transition_closeout import build_p34_governance_transition_completion_gate
from btc_finance_platform.paper_governance_transition_closeout import build_p34_governance_transition_final_packet


if __name__ == "__main__":
 result = {
  "governance_transition_closeout": build_p34_governance_transition_closeout(),
  "governance_transition_final_packet": build_p34_governance_transition_final_packet(),
  "governance_transition_completion_gate": build_p34_governance_transition_completion_gate(),
 }
 print(json.dumps(result, indent=2, sort_keys=True))
