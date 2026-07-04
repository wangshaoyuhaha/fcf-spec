import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_release_guard_manifest import build_p43_governance_release_guard_manifest
from btc_finance_platform.paper_governance_release_guard_manifest import build_p43_release_guard_boundary_manifest
from btc_finance_platform.paper_governance_release_guard_manifest import build_p43_release_guard_gate_manifest

if __name__ == "__main__":
    result = {
        "manifest": build_p43_governance_release_guard_manifest(),
        "boundary": build_p43_release_guard_boundary_manifest(),
        "gate": build_p43_release_guard_gate_manifest(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
