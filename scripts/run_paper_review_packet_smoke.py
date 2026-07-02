import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_review_packet import build_paper_analysis_review_packet
from btc_finance_platform.paper_review_packet import write_paper_analysis_review_packet


if __name__ == "__main__":
    root = Path(ROOT)
    sources = [
        root / "fixtures" / "sample_paper_batch.json",
        root / "fixtures" / "sample_paper_batch.csv",
    ]
    output = root / "artifacts" / "paper_analysis_review_packet.json"

    packet = build_paper_analysis_review_packet(sources)
    written = write_paper_analysis_review_packet(sources, output)

    print(json.dumps({
        "packet": packet,
        "written": {
            "ok": written["ok"],
            "type": written["type"],
            "output_file": written["output_file"],
            "paper_only": written["paper_only"],
            "operator_review_required": written["operator_review_required"],
        },
    }, indent=2, sort_keys=True))
