import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_phase_transition_acceptance import build_p33_transition_acceptance_lock
from btc_finance_platform.paper_phase_transition_acceptance import build_p33_transition_acceptance_packet
from btc_finance_platform.paper_phase_transition_acceptance import build_p33_transition_completion_receipt


if __name__ == "__main__":
    result = {
        "transition_acceptance_packet": build_p33_transition_acceptance_packet(),
        "transition_acceptance_lock": build_p33_transition_acceptance_lock(),
        "transition_completion_receipt": build_p33_transition_completion_receipt(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
