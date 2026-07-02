import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.analysis_flow import run_paper_analysis_flow


if __name__ == "__main__":
    result = run_paper_analysis_flow({
        "symbol": "BTCUSDT",
        "price": 65000,
        "reference_price": 64000,
    })

    print(json.dumps(result, indent=2, sort_keys=True))
