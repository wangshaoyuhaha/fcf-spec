import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_next_phase_continuity import build_p32_continuity_audit
from btc_finance_platform.paper_next_phase_continuity import build_p32_continuity_gate
from btc_finance_platform.paper_next_phase_continuity import build_p32_continuity_map


if __name__ == "__main__":
    result = {
        "continuity_map": build_p32_continuity_map(),
        "continuity_audit": build_p32_continuity_audit(),
        "continuity_gate": build_p32_continuity_gate(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
