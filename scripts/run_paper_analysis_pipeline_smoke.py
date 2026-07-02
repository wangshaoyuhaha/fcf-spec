import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.local_data_handoff import build_local_analysis_handoff_package
from btc_finance_platform.paper_analysis_pipeline import build_paper_analysis_pipeline_report
from btc_finance_platform.paper_analysis_pipeline import run_paper_analysis_from_handoff_package
from btc_finance_platform.paper_analysis_pipeline import run_paper_analysis_from_local_files


if __name__ == "__main__":
    root = Path(ROOT)
    sources = [
        root / "fixtures" / "sample_paper_batch.json",
        root / "fixtures" / "sample_paper_batch.csv",
    ]

    handoff = build_local_analysis_handoff_package(sources)
    from_handoff = run_paper_analysis_from_handoff_package(handoff)
    from_files = run_paper_analysis_from_local_files(sources)
    report = build_paper_analysis_pipeline_report(sources)

    print(json.dumps({
        "from_handoff": from_handoff,
        "from_files": from_files,
        "report": report,
    }, indent=2, sort_keys=True))
