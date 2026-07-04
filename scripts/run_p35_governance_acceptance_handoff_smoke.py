import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
 sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_acceptance_handoff import build_p35_acceptance_next_gate
from btc_finance_platform.paper_governance_acceptance_handoff import build_p35_acceptance_operator_packet
from btc_finance_platform.paper_governance_acceptance_handoff import build_p35_governance_acceptance_handoff


if __name__ == "__main__":
 result = {
  "governance_acceptance_handoff": build_p35_governance_acceptance_handoff(),
  "acceptance_operator_packet": build_p35_acceptance_operator_packet(),
  "acceptance_next_gate": build_p35_acceptance_next_gate(),
 }
 print(json.dumps(result, indent=2, sort_keys=True))
