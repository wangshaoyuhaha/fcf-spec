import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_scenario_engine import write_scenario_engine_report


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "learning_engine" / "scenario_engine_report.json"

    scenarios = [
        {
            "scenario_id": "trend_up_normal",
            "scenario_name": "trend up normal continuation",
            "regime": "trend_up",
            "shock_type": "none",
            "paper_return_pct": 0.08,
            "max_paper_drawdown_pct": 0.04,
            "liquidity_stress": False,
        },
        {
            "scenario_id": "liquidity_stress_gap",
            "scenario_name": "liquidity stress gap down",
            "regime": "liquidity_stress",
            "shock_type": "gap_down",
            "paper_return_pct": -0.04,
            "max_paper_drawdown_pct": 0.18,
            "liquidity_stress": True,
        },
    ]

    result = write_scenario_engine_report(
        "governor_weight_proposal_001",
        scenarios,
        output,
    )

    report = result["report"]

    if report["scenario_policy"]["auto_accept_allowed"] is not False:
        raise SystemExit("scenario engine must not auto-accept proposals")

    if report["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    if report["operator_review_required"] is not True:
        raise SystemExit("operator review must remain required")

    print(json.dumps(result, indent=2, sort_keys=True))
