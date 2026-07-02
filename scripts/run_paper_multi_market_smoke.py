import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_multi_market import build_multi_market_batch_contract
from btc_finance_platform.paper_multi_market import extract_analysis_compatible_items
from btc_finance_platform.paper_multi_market import get_asset_class_taxonomy


if __name__ == "__main__":
    root = Path(ROOT)
    fixture = root / "fixtures" / "sample_multi_market_batch.json"
    items = json.loads(fixture.read_text(encoding="utf-8-sig"))

    taxonomy = get_asset_class_taxonomy()
    contract = build_multi_market_batch_contract(items)
    analysis_items = extract_analysis_compatible_items(contract)

    print(json.dumps({
        "taxonomy": taxonomy,
        "contract": contract,
        "analysis_items": analysis_items,
    }, indent=2, sort_keys=True))
