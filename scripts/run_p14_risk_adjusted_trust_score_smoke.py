import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_risk_adjusted_trust_score import write_risk_adjusted_trust_report


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "learning_engine" / "risk_adjusted_trust_report.json"

    observations = [
        {
            "expert_id": "smooth_momentum_expert",
            "regime": "trend_up",
            "direction": "long",
            "outcome": "win",
            "confidence": 0.72,
            "age_days": 1,
            "max_paper_drawdown_pct": 0.02,
        },
        {
            "expert_id": "deep_drawdown_expert",
            "regime": "trend_up",
            "direction": "long",
            "outcome": "win",
            "confidence": 0.72,
            "age_days": 1,
            "max_paper_drawdown_pct": 0.30,
        },
    ]

    result = write_risk_adjusted_trust_report(observations, output)
    report = result["report"]

    if report["report_status"] != "READY_FOR_OPERATOR_REVIEW":
        raise SystemExit("risk-adjusted trust report must wait for operator review")

    if report["governor_weight_auto_apply_allowed"] is not False:
        raise SystemExit("governor weights must not auto-apply")

    if report["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    print(json.dumps(result, indent=2, sort_keys=True))
