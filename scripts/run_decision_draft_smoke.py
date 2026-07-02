import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.decision_draft import (
    assert_paper_decision_draft,
    create_paper_decision_draft,
)
from btc_finance_platform.market_snapshot import create_paper_market_snapshot


if __name__ == "__main__":
    snapshot = create_paper_market_snapshot("BTCUSDT", 65000.0)
    draft = create_paper_decision_draft(snapshot)
    assert_paper_decision_draft(draft)
    print(json.dumps(draft, indent=2, sort_keys=True))
