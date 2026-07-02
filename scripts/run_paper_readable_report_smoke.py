import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_readable_report import build_paper_analysis_markdown_report
from btc_finance_platform.paper_readable_report import write_paper_analysis_report_bundle


if __name__ == "__main__":
    root = Path(ROOT)
    sources = [
        root / "fixtures" / "sample_paper_batch.json",
        root / "fixtures" / "sample_paper_batch.csv",
    ]
    output_dir = root / "artifacts" / "paper_readable_report"

    report = build_paper_analysis_markdown_report(sources)
    bundle = write_paper_analysis_report_bundle(sources, output_dir)

    print(json.dumps({
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
            "json_file": bundle["json_file"],
            "paper_only": bundle["paper_only"],
            "operator_review_required": bundle["operator_review_required"],
        },
    }, indent=2, sort_keys=True))
