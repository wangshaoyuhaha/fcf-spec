import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_final_acceptance_lock_handoff import build_p45_governance_final_acceptance_lock_handoff
from btc_finance_platform.paper_governance_final_acceptance_lock_handoff import build_p45_final_acceptance_lock_boundary_handoff
from btc_finance_platform.paper_governance_final_acceptance_lock_handoff import build_p45_final_acceptance_lock_gate_handoff

if __name__ == "__main__":
    result = {
        "handoff": build_p45_governance_final_acceptance_lock_handoff(),
        "boundary": build_p45_final_acceptance_lock_boundary_handoff(),
        "gate": build_p45_final_acceptance_lock_gate_handoff(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
