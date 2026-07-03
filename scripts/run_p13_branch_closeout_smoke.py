import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p13_branch_closeout import write_p13_branch_closeout_manifest


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "operator_console" / "index.html"
    manifest_path = Path(ROOT) / "runtime" / "operator_console" / "p13_branch_closeout_manifest.json"

    result = write_p13_branch_closeout_manifest(output, manifest_path)
    manifest = result["manifest"]

    if manifest["closeout_status"] != "READY_FOR_BRANCH_REVIEW":
        raise SystemExit("P13 branch closeout status is invalid")

    if manifest["merge_to_main_completed"] is not False:
        raise SystemExit("merge must not be marked completed")

    if manifest["release_created"] is not False:
        raise SystemExit("release must not be marked created")

    if manifest["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    print(json.dumps(result, indent=2, sort_keys=True))
