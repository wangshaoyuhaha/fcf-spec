import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
 sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_transition_handoff import build_p34_governance_transition_handoff
from btc_finance_platform.paper_governance_transition_handoff import build_p34_governance_transition_next_gate
from btc_finance_platform.paper_governance_transition_handoff import build_p34_governance_transition_operator_packet


if __name__ == "__main__":
 result = {
  "governance_transition_handoff": build_p34_governance_transition_handoff(),
  "governance_transition_operator_packet": build_p34_governance_transition_operator_packet(),
  "governance_transition_next_gate": build_p34_governance_transition_next_gate(),
 }
 print(json.dumps(result, indent=2, sort_keys=True))
