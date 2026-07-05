import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from data_app.local_file_adapter import build_local_file_adapter_contract
from data_app.local_file_adapter import build_local_file_adapter_result


if __name__ == "__main__":
    root = Path(ROOT)
    csv_file = root / "data_app" / "fixtures" / "a_share_sample.csv"
    json_file = root / "data_app" / "fixtures" / "a_share_sample.json"
    print(json.dumps({
        "status": "completed",
        "runner": "data_app_local_file_adapter_smoke",
        "contract": build_local_file_adapter_contract(),
        "csv_result": build_local_file_adapter_result(csv_file),
        "json_result": build_local_file_adapter_result(json_file),
    }, indent=2, sort_keys=True))
