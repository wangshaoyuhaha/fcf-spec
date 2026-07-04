import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_terminal_handoff import build_p31_terminal_checkpoint
from btc_finance_platform.paper_release_terminal_handoff import build_p31_terminal_export_packet
from btc_finance_platform.paper_release_terminal_handoff import build_p31_terminal_handoff_packet


if __name__ == "__main__":
    result = {
        "export_packet": build_p31_terminal_export_packet(),
        "checkpoint": build_p31_terminal_checkpoint(),
        "handoff": build_p31_terminal_handoff_packet(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
