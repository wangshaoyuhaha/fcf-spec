import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from data_app.health_check import build_data_app_health_check
from data_app.health_check import route_by_health_check_state


if __name__ == "__main__":
    root = Path(ROOT)
    csv_file = root / "data_app" / "fixtures" / "a_share_sample.csv"
    health = build_data_app_health_check(csv_file)
    route = route_by_health_check_state(health)
    print(json.dumps({
        "status": "completed",
        "runner": "data_app_health_check_smoke",
        "health_check": health,
        "route": route,
    }, indent=2, sort_keys=True))
