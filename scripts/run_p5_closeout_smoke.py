import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_closeout import build_p5_closeout_package
from btc_finance_platform.paper_governance_closeout import get_p5_governance_layer_capabilities
from btc_finance_platform.paper_governance_closeout import get_p5_safety_acceptance
from btc_finance_platform.paper_governance_closeout import get_p5_to_p6_transition_anchor


if __name__ == "__main__":
    root = Path(ROOT)
    sources = [
        root / "fixtures" / "sample_paper_batch.json",
        root / "fixtures" / "sample_paper_batch.csv",
    ]

    result = {
        "capabilities": get_p5_governance_layer_capabilities(),
        "safety": get_p5_safety_acceptance(),
        "transition": get_p5_to_p6_transition_anchor(),
        "closeout": build_p5_closeout_package(sources),
    }

    print(json.dumps(result, indent=2, sort_keys=True))
