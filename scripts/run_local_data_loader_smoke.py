import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.local_data_loader import build_local_data_manifest
from btc_finance_platform.local_data_loader import load_paper_batch_from_file


if __name__ == "__main__":
    root = Path(ROOT)
    json_fixture = root / "fixtures" / "sample_paper_batch.json"
    csv_fixture = root / "fixtures" / "sample_paper_batch.csv"

    json_loaded = load_paper_batch_from_file(json_fixture)
    csv_loaded = load_paper_batch_from_file(csv_fixture)
    manifest = build_local_data_manifest([json_fixture, csv_fixture])

    print(json.dumps({
        "json_loaded": json_loaded,
        "csv_loaded": csv_loaded,
        "manifest": manifest,
    }, indent=2, sort_keys=True))
