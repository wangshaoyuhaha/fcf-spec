import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_analysis_logic import analyze_paper_batch
from btc_finance_platform.paper_analysis_logic import draft_paper_signal


if __name__ == "__main__":
    single = draft_paper_signal(
        symbol="BTCUSDT",
        price=65000,
        reference_price=64000,
        price_history=[63000, 64000, 65000],
    )

    batch = analyze_paper_batch([
        {"symbol": "BTCUSDT", "price": 65000, "reference_price": 64000},
        {"symbol": "ETHUSDT", "price": 3500, "reference_price": 3600},
    ])

    print(json.dumps({
        "single": single,
        "batch": batch,
    }, indent=2, sort_keys=True))
