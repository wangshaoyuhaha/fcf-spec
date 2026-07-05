import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from stock_app.contracts.stock_app_closeout import build_stock_app_1_handoff_packet


if __name__ == "__main__":
    print(json.dumps(build_stock_app_1_handoff_packet(), indent=2, sort_keys=True))
