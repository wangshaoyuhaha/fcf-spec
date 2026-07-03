import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_patch_proposal_sandbox import build_patch_proposal
from btc_finance_platform.p14_patch_proposal_sandbox import write_patch_proposal


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "learning_engine" / "patch_proposal_record.json"

    proposal = build_patch_proposal(
        proposal_id="patch_proposal_001",
        title="tighten paper feature audit threshold",
        rationale="paper-only audit found weak feature overlap requiring operator review",
        target_files=[
            "src/btc_finance_platform/p14_feature_source_audit.py",
            "tests/test_p14_feature_source_audit.py",
        ],
        test_plan=[
            "python scripts/run_all_checks.py",
            "python -m pytest -q",
        ],
        risk_notes=[
            "proposal-only",
            "no auto apply",
            "operator review required",
        ],
    )

    result = write_patch_proposal(proposal, output)
    record = result["record"]

    if record["gate"]["gate_status"] != "passed":
        raise SystemExit("patch proposal gate should pass")

    if record["patch_auto_apply_allowed"] is not False:
        raise SystemExit("patch auto apply must remain false")

    if record["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    print(json.dumps(result, indent=2, sort_keys=True))
