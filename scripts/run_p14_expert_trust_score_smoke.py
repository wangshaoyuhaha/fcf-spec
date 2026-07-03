import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_expert_trust_score import write_expert_trust_report


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "learning_engine" / "expert_trust_report.json"

    observations = [
        {
            "expert_id": "momentum_expert",
            "regime": "trend_up",
            "direction": "long",
            "outcome": "win",
            "confidence": 0.72,
            "age_days": 1,
        },
        {
            "expert_id": "macro_expert",
            "regime": "trend_up",
            "direction": "observe",
            "outcome": "neutral",
            "confidence": 0.55,
            "age_days": 1,
        },
        {
            "expert_id": "smc_expert",
            "regime": "trend_up",
            "direction": "flat",
            "outcome": "loss",
            "confidence": 0.61,
            "age_days": 1,
        },
    ]

    result = write_expert_trust_report(observations, output)
    report = result["report"]

    if report["report_status"] != "READY_FOR_OPERATOR_REVIEW":
        raise SystemExit("trust report must wait for operator review")

    if report["governor_weight_auto_apply_allowed"] is not False:
        raise SystemExit("governor weights must not auto-apply")

    if report["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    print(json.dumps(result, indent=2, sort_keys=True))
