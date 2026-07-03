import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_final_archive_manifest import default_final_archive_items
from btc_finance_platform.p14_final_archive_manifest import write_final_archive_manifest


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "learning_engine" / "p14_final_archive_manifest.json"

    result = write_final_archive_manifest(
        source_branch="p13-operator-console",
        target_branch="main",
        validation_passed_count=591,
        archive_items=default_final_archive_items(),
        path=output,
    )

    manifest = result["manifest"]

    if manifest["archive_status"] != "READY_FOR_FINAL_OPERATOR_ARCHIVE_REVIEW":
        raise SystemExit("archive manifest must be ready only for operator archive review")

    if manifest["archive_policy"]["merge_to_main_allowed_now"] is not False:
        raise SystemExit("merge to main must remain false")

    if manifest["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    print(json.dumps(result, indent=2, sort_keys=True))
