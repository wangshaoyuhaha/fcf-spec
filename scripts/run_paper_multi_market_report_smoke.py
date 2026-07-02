import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_multi_market_report import build_multi_market_markdown_report
from btc_finance_platform.paper_multi_market_report import build_multi_market_ui_contract
from btc_finance_platform.paper_multi_market_report import write_multi_market_report_bundle

if __name__ == "__main__":
    root = Path(ROOT)
    fixture = root / "fixtures" / "sample_multi_market_batch.json"
    output_dir = root / "artifacts" / "multi_market_report_bundle"
    contract = build_multi_market_ui_contract(fixture)
    report = build_multi_market_markdown_report(fixture)
    bundle = write_multi_market_report_bundle(fixture, output_dir)
    print(json.dumps({
        "contract": {
            "ok": contract["ok"],
            "type": contract["type"],
            "count": contract["count"],
            "status_counts": contract["status_counts"],
            "validation": contract["validation"],
        },
        "report": {
            "ok": report["ok"],
            "type": report["type"],
            "summary": report["summary"],
            "paper_only": report["paper_only"],
            "operator_review_required": report["operator_review_required"],
        },
        "bundle": {
            "ok": bundle["ok"],
            "type": bundle["type"],
            "output_dir": bundle["output_dir"],
            "markdown_file": bundle["markdown_file"],
            "contract_file": bundle["contract_file"],
            "summary_file": bundle["summary_file"],
        },
    }, indent=2, sort_keys=True))
