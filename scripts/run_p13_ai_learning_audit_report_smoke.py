import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p13_ai_learning_audit_report import write_ai_learning_audit_report


if __name__ == "__main__":
    ledger = Path(ROOT) / "runtime" / "operator_console" / "ai_learning_memory_ledger.json"
    report = Path(ROOT) / "runtime" / "operator_console" / "ai_learning_audit_report.json"

    result = write_ai_learning_audit_report(ledger, report)
    audit = result["report"]

    if audit["audit_status"] != "READY_FOR_OPERATOR_REVIEW":
        raise SystemExit("audit report must wait for operator review")

    if audit["patch_policy"]["patch_auto_apply_allowed"] is not False:
        raise SystemExit("patch auto apply must remain false")

    if audit["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    print(json.dumps(result, indent=2, sort_keys=True))
