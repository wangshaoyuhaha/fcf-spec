import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.analysis_flow import run_paper_analysis_flow
from btc_finance_platform.paper_history import save_paper_run_record, summarize_paper_history


if __name__ == "__main__":
    result = run_paper_analysis_flow({
        "symbol": "BTCUSDT",
        "price": 65000,
        "reference_price": 64000,
    })

    with tempfile.TemporaryDirectory() as temp_dir:
        saved = save_paper_run_record(result["record"], temp_dir)
        summary = summarize_paper_history(temp_dir)

    print(json.dumps({
        "saved": saved,
        "summary": summary,
    }, indent=2, sort_keys=True))
