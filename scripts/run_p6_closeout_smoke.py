import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_multi_market_closeout import build_p6_closeout_package
from btc_finance_platform.paper_multi_market_closeout import get_p6_multi_market_capabilities
from btc_finance_platform.paper_multi_market_closeout import get_p6_safety_acceptance
from btc_finance_platform.paper_multi_market_closeout import get_p6_to_p7_transition_anchor

if __name__ == "__main__":
    root = Path(ROOT)
    fixture = root / "fixtures" / "sample_multi_market_batch.json"
    result = {
        "capabilities": get_p6_multi_market_capabilities(),
        "safety": get_p6_safety_acceptance(),
        "transition": get_p6_to_p7_transition_anchor(),
        "closeout": build_p6_closeout_package(fixture),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
