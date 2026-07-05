import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from data_app.closeout import build_data_app_1_closeout_summary


if __name__ == "__main__":
    print(json.dumps({
        "status": "completed",
        "runner": "data_app_1_closeout_smoke",
        "summary": build_data_app_1_closeout_summary(),
    }, indent=2, sort_keys=True))
