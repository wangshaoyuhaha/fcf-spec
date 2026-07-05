import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from data_app.universe import build_data_app_universe_contract
from data_app.universe import build_data_app_universe_package


if __name__ == "__main__":
    root = Path(ROOT)
    csv_file = root / "data_app" / "fixtures" / "a_share_sample.csv"
    package = build_data_app_universe_package(csv_file)
    print(json.dumps({
        "status": "completed",
        "runner": "data_app_universe_smoke",
        "contract": build_data_app_universe_contract(),
        "package": package,
    }, indent=2, sort_keys=True))
