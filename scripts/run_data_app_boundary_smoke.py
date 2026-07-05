import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from data_app.boundary import build_data_app_sidecar_boundary
from data_app.boundary import validate_data_app_sidecar_boundary


if __name__ == "__main__":
    boundary = build_data_app_sidecar_boundary()
    validation = validate_data_app_sidecar_boundary(boundary)
    print(json.dumps({
        "status": "completed",
        "runner": "data_app_boundary_smoke",
        "boundary": boundary,
        "validation": validation,
    }, indent=2, sort_keys=True))
