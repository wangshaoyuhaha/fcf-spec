import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_final_acceptance_lock_closeout import build_p45_governance_final_acceptance_lock_closeout
from btc_finance_platform.paper_governance_final_acceptance_lock_closeout import build_p45_final_acceptance_lock_boundary_closeout
from btc_finance_platform.paper_governance_final_acceptance_lock_closeout import build_p45_final_acceptance_lock_gate_closeout

if __name__ == "__main__":
    result = {
        "closeout": build_p45_governance_final_acceptance_lock_closeout(),
        "boundary": build_p45_final_acceptance_lock_boundary_closeout(),
        "gate": build_p45_final_acceptance_lock_gate_closeout(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
