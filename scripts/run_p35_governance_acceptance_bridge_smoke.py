import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
 sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_acceptance_bridge import build_p35_acceptance_readiness_gate
from btc_finance_platform.paper_governance_acceptance_bridge import build_p35_governance_acceptance_bridge
from btc_finance_platform.paper_governance_acceptance_bridge import build_p35_operator_acceptance_boundary


if __name__ == "__main__":
 result = {
  "governance_acceptance_bridge": build_p35_governance_acceptance_bridge(),
  "operator_acceptance_boundary": build_p35_operator_acceptance_boundary(),
  "acceptance_readiness_gate": build_p35_acceptance_readiness_gate(),
 }
 print(json.dumps(result, indent=2, sort_keys=True))
