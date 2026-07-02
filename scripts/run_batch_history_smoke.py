import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.batch_analysis import run_paper_analysis_batch, summarize_batch_results
from btc_finance_platform.batch_history import create_batch_run_record, save_batch_run_record, summarize_batch_history
from btc_finance_platform.batch_report import render_batch_report


if __name__ == "__main__":
    batch = run_paper_analysis_batch([
        {"symbol": "BTCUSDT", "price": 65000, "reference_price": 64000},
        {"symbol": "ETHUSDT", "price": 3500, "reference_price": 3600},
    ])
    summary = summarize_batch_results(batch)
    report = render_batch_report(batch, summary)
    record = create_batch_run_record(batch, summary, report)

    with tempfile.TemporaryDirectory() as temp_dir:
        saved = save_batch_run_record(record, temp_dir)
        history = summarize_batch_history(temp_dir)

    print(json.dumps({
        "record": record,
        "saved": saved,
        "history": history,
    }, indent=2, sort_keys=True))
