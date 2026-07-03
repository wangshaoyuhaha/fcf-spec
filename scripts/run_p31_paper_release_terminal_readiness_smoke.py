import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_terminal_readiness import build_p31_terminal_completion_gate
from btc_finance_platform.paper_release_terminal_readiness import build_p31_terminal_readable_report
from btc_finance_platform.paper_release_terminal_readiness import build_p31_terminal_readiness_checklist


if __name__ == "__main__":
    result = {
        "report": build_p31_terminal_readable_report(),
        "checklist": build_p31_terminal_readiness_checklist(),
        "completion_gate": build_p31_terminal_completion_gate(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
