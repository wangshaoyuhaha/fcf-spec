import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_next_phase_acceptance import build_p32_acceptance_lock
from btc_finance_platform.paper_next_phase_acceptance import build_p32_acceptance_packet
from btc_finance_platform.paper_next_phase_acceptance import build_p32_acceptance_receipt


if __name__ == "__main__":
    result = {
        "acceptance_packet": build_p32_acceptance_packet(),
        "acceptance_lock": build_p32_acceptance_lock(),
        "acceptance_receipt": build_p32_acceptance_receipt(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
