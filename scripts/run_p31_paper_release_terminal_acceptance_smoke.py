import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_terminal_acceptance import build_p31_terminal_acceptance_packet
from btc_finance_platform.paper_release_terminal_acceptance import build_p31_terminal_completion_receipt
from btc_finance_platform.paper_release_terminal_acceptance import build_p31_terminal_release_lock


if __name__ == "__main__":
    result = {
        "acceptance_packet": build_p31_terminal_acceptance_packet(),
        "release_lock": build_p31_terminal_release_lock(),
        "completion_receipt": build_p31_terminal_completion_receipt(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
