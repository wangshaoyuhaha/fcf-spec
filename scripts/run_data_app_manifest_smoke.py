import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from data_app.manifest import build_data_app_manifest_for_file
from data_app.manifest import build_data_app_manifest_for_files
from data_app.manifest import validate_data_app_manifest


if __name__ == "__main__":
    root = Path(ROOT)
    csv_file = root / "data_app" / "fixtures" / "a_share_sample.csv"
    json_file = root / "data_app" / "fixtures" / "a_share_sample.json"
    csv_manifest = build_data_app_manifest_for_file(csv_file)
    batch_manifest = build_data_app_manifest_for_files([csv_file, json_file])
    print(json.dumps({
        "status": "completed",
        "runner": "data_app_manifest_smoke",
        "csv_manifest": csv_manifest,
        "csv_validation": validate_data_app_manifest(csv_manifest),
        "batch_manifest": batch_manifest,
        "batch_validation": validate_data_app_manifest(batch_manifest),
    }, indent=2, sort_keys=True))
