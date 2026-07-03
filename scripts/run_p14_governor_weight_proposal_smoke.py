import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_governor_weight_proposal import write_governor_weight_proposal


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "learning_engine" / "governor_weight_proposal.json"

    rows = [
        {"expert_id": "momentum_expert", "regime": "trend_up", "risk_adjusted_score": 0.70},
        {"expert_id": "macro_expert", "regime": "trend_up", "risk_adjusted_score": 0.20},
        {"expert_id": "smc_expert", "regime": "trend_up", "risk_adjusted_score": -0.10},
    ]

    result = write_governor_weight_proposal(
        rows,
        regime="trend_up",
        meta_anomaly_status="heightened_operator_review",
        path=output,
    )

    proposal = result["proposal"]

    if proposal["proposal_status"] != "READY_FOR_OPERATOR_REVIEW":
        raise SystemExit("proposal must wait for operator review")

    if proposal["proposal_policy"]["governor_weight_auto_apply_allowed"] is not False:
        raise SystemExit("governor weights must not auto-apply")

    if proposal["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    print(json.dumps(result, indent=2, sort_keys=True))
