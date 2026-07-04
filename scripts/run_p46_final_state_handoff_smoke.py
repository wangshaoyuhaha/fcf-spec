import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_p46_final_state_handoff import build_p46_architecture_index
from btc_finance_platform.paper_p46_final_state_handoff import build_p46_final_project_state
from btc_finance_platform.paper_p46_final_state_handoff import build_p46_final_state_closeout
from btc_finance_platform.paper_p46_final_state_handoff import build_p46_handoff_packet

if __name__ == "__main__":
    result = {
        "final_project_state": build_p46_final_project_state(),
        "handoff_packet": build_p46_handoff_packet(),
        "architecture_index": build_p46_architecture_index(),
        "final_state_closeout": build_p46_final_state_closeout(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
