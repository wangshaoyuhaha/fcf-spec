import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_phase_transition_manifest import build_p33_manifest_gate
from btc_finance_platform.paper_phase_transition_manifest import build_p33_transition_checkpoint
from btc_finance_platform.paper_phase_transition_manifest import build_p33_transition_manifest


if __name__ == "__main__":
    result = {
        "transition_manifest": build_p33_transition_manifest(),
        "transition_checkpoint": build_p33_transition_checkpoint(),
        "manifest_gate": build_p33_manifest_gate(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
