import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_p47_final_consistency_audit import build_p47_final_consistency_closeout
from btc_finance_platform.paper_p47_final_consistency_audit import build_p47_phase_file_matrix
from btc_finance_platform.paper_p47_final_consistency_audit import build_p47_safety_boundary_audit
from btc_finance_platform.paper_p47_final_consistency_audit import build_p47_serialization_audit

if __name__ == "__main__":
    result = {
        "phase_file_matrix": build_p47_phase_file_matrix(),
        "serialization_audit": build_p47_serialization_audit(),
        "safety_boundary_audit": build_p47_safety_boundary_audit(),
        "final_consistency_closeout": build_p47_final_consistency_closeout(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
