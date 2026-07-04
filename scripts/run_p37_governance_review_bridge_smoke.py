import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
 sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_review_bridge import build_p37_governance_review_bridge
from btc_finance_platform.paper_governance_review_bridge import build_p37_review_boundary
from btc_finance_platform.paper_governance_review_bridge import build_p37_review_readiness_gate


if __name__ == "__main__":
 result = {
  "governance_review_bridge": build_p37_governance_review_bridge(),
  "review_boundary": build_p37_review_boundary(),
  "review_readiness_gate": build_p37_review_readiness_gate(),
 }
 print(json.dumps(result, indent=2, sort_keys=True))
