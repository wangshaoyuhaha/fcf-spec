import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_operator_review import build_p31_next_phase_gate
from btc_finance_platform.paper_release_operator_review import build_p31_no_release_guard
from btc_finance_platform.paper_release_operator_review import build_p31_operator_review_packet


if __name__ == "__main__":
    result = {
        "review_packet": build_p31_operator_review_packet(),
        "no_release_guard": build_p31_no_release_guard(),
        "next_phase_gate": build_p31_next_phase_gate(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
