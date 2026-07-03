import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_shadow_ledger import append_shadow_ledger_event
from btc_finance_platform.p14_shadow_ledger import summarize_shadow_ledger


if __name__ == "__main__":
    ledger = Path(ROOT) / "runtime" / "learning_engine" / "shadow_ledger.json"

    result = append_shadow_ledger_event(
        ledger,
        "paper_decision_001",
        "trend_up",
        [
            {
                "expert_id": "macro_expert",
                "direction": "observe",
                "confidence": 0.55,
                "rationale": "paper-only macro uncertainty",
            },
            {
                "expert_id": "momentum_expert",
                "direction": "long",
                "confidence": 0.72,
                "rationale": "paper-only momentum continuation",
            },
            {
                "expert_id": "smc_expert",
                "direction": "flat",
                "confidence": 0.61,
                "rationale": "paper-only liquidity sweep risk",
            },
        ],
        selected_expert_id="momentum_expert",
    )

    summary = summarize_shadow_ledger(ledger)

    if result["latest_event"]["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    if summary["event_count"] < 1:
        raise SystemExit("shadow ledger should contain events")

    if "momentum_expert" not in summary["expert_counts"]:
        raise SystemExit("expert proposal should be counted")

    print(json.dumps({"append": result, "summary": summary}, indent=2, sort_keys=True))
