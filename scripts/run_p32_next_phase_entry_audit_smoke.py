import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_next_phase_entry_audit import build_p32_entry_packet
from btc_finance_platform.paper_next_phase_entry_audit import build_p32_entry_readiness_gate
from btc_finance_platform.paper_next_phase_entry_audit import build_p32_entry_safety_audit


if __name__ == "__main__":
    result = {
        "entry_packet": build_p32_entry_packet(),
        "safety_audit": build_p32_entry_safety_audit(),
        "readiness_gate": build_p32_entry_readiness_gate(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
