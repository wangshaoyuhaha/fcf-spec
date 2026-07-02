import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.local_data_bridge import build_local_data_audit_report
from btc_finance_platform.local_data_bridge import build_local_paper_analysis_inputs
from btc_finance_platform.local_data_bridge import build_local_paper_dataset


if __name__ == "__main__":
    root = Path(ROOT)
    json_fixture = root / "fixtures" / "sample_paper_batch.json"
    csv_fixture = root / "fixtures" / "sample_paper_batch.csv"
    sources = [json_fixture, csv_fixture]

    dataset = build_local_paper_dataset(sources)
    analysis_inputs = build_local_paper_analysis_inputs(sources)
    audit_report = build_local_data_audit_report(sources)

    print(json.dumps({
        "dataset": dataset,
        "analysis_inputs": analysis_inputs,
        "audit_report": audit_report,
    }, indent=2, sort_keys=True))
