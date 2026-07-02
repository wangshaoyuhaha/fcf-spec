import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.market_snapshot import create_paper_market_snapshot


if __name__ == "__main__":
    snapshot = create_paper_market_snapshot("BTCUSDT", 65000.0)
    print(json.dumps(snapshot, indent=2, sort_keys=True))
