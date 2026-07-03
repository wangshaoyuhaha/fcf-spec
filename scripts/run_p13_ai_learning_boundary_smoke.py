import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p13_ai_learning_boundary import write_ai_learning_self_audit_boundary


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "operator_console" / "ai_learning_self_audit_boundary.json"
    result = write_ai_learning_self_audit_boundary(output)
    boundary = result["boundary"]

    if boundary["learning_enabled"] is not True:
        raise SystemExit("learning boundary should be enabled")

    if boundary["patch_auto_apply_allowed"] is not False:
        raise SystemExit("patch auto apply must remain false")

    if boundary["operator_review_required"] is not True:
        raise SystemExit("operator review must remain required")

    if boundary["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    print(json.dumps(result, indent=2, sort_keys=True))
