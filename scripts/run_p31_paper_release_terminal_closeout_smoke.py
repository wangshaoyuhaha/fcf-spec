import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_terminal_closeout import build_p31_terminal_packet
from btc_finance_platform.paper_release_terminal_closeout import build_p31_terminal_safety_gate
from btc_finance_platform.paper_release_terminal_closeout import build_p31_terminal_summary


if __name__ == "__main__":
    result = {
        "packet": build_p31_terminal_packet(),
        "summary": build_p31_terminal_summary(),
        "safety_gate": build_p31_terminal_safety_gate(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
