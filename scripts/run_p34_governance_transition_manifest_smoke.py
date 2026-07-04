import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_transition_manifest import build_p34_governance_manifest_gate
from btc_finance_platform.paper_governance_transition_manifest import build_p34_governance_transition_checkpoint
from btc_finance_platform.paper_governance_transition_manifest import build_p34_governance_transition_manifest


if __name__ == "__main__":
    result = {
        "governance_transition_manifest": build_p34_governance_transition_manifest(),
        "governance_transition_checkpoint": build_p34_governance_transition_checkpoint(),
        "governance_manifest_gate": build_p34_governance_manifest_gate(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
