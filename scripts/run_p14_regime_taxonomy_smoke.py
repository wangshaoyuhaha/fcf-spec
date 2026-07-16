import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_regime_taxonomy import classify_regime
from btc_finance_platform.p14_regime_taxonomy import write_regime_taxonomy


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "learning_engine" / "regime_taxonomy.json"
    result = write_regime_taxonomy(output)

    sample = classify_regime(
        {
            "trend": "up",
            "volatility": "high",
            "liquidity": "normal",
        }
    )

    if sample["regime"] != "high_volatility_breakout":
        raise SystemExit("sample regime classification failed")

    if result["taxonomy"]["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    print(json.dumps({"taxonomy": result, "sample": sample}, indent=2, sort_keys=True))
