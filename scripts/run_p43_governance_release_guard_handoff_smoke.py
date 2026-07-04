import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_release_guard_handoff import build_p43_governance_release_guard_handoff
from btc_finance_platform.paper_governance_release_guard_handoff import build_p43_release_guard_boundary_handoff
from btc_finance_platform.paper_governance_release_guard_handoff import build_p43_release_guard_gate_handoff

if __name__ == "__main__":
    result = {
        "handoff": build_p43_governance_release_guard_handoff(),
        "boundary": build_p43_release_guard_boundary_handoff(),
        "gate": build_p43_release_guard_gate_handoff(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
