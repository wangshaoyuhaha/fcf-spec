import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_feature_orthogonality_audit import write_feature_orthogonality_audit_report


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "learning_engine" / "feature_orthogonality_audit_report.json"

    pairs = [
        {
            "feature_a": "rsi_14",
            "feature_b": "kdj_k",
            "correlation": 0.91,
            "cost_a": 1.0,
            "cost_b": 2.0,
            "latency_a_ms": 5,
            "latency_b_ms": 20,
        },
        {
            "feature_a": "volume_breakout_score",
            "feature_b": "macro_uncertainty_note",
            "correlation": 0.18,
            "cost_a": 1.0,
            "cost_b": 3.0,
        },
    ]

    result = write_feature_orthogonality_audit_report(pairs, output)
    report = result["report"]

    if report["audit_status"] != "READY_FOR_OPERATOR_REVIEW":
        raise SystemExit("orthogonality audit must wait for operator review")

    if report["audit_policy"]["auto_prune_allowed"] is not False:
        raise SystemExit("auto prune must remain false")

    if report["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    print(json.dumps(result, indent=2, sort_keys=True))
