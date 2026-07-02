import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.local_data_handoff import build_local_analysis_handoff_package
from btc_finance_platform.local_data_handoff import build_local_data_quality_gate


if __name__ == "__main__":
    root = Path(ROOT)
    sources = [
        root / "fixtures" / "sample_paper_batch.json",
        root / "fixtures" / "sample_paper_batch.csv",
    ]

    quality_gate = build_local_data_quality_gate(sources)
    handoff_package = build_local_analysis_handoff_package(sources)

    print(json.dumps({
        "quality_gate": quality_gate,
        "handoff_package": handoff_package,
    }, indent=2, sort_keys=True))
