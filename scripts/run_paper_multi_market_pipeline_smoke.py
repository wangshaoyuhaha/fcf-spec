import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_multi_market_pipeline import build_multi_market_pipeline_report_from_json
from btc_finance_platform.paper_multi_market_pipeline import write_multi_market_pipeline_report

if __name__ == "__main__":
    root = Path(ROOT)
    fixture = root / "fixtures" / "sample_multi_market_batch.json"
    output = root / "artifacts" / "multi_market_pipeline_report.json"
    report = build_multi_market_pipeline_report_from_json(fixture)
    written = write_multi_market_pipeline_report(fixture, output)
    print(json.dumps({
        "report": report,
        "written": {
            "ok": written["ok"],
            "type": written["type"],
            "output_file": written["output_file"],
            "paper_only": written["paper_only"],
            "operator_review_required": written["operator_review_required"],
        },
    }, indent=2, sort_keys=True))
