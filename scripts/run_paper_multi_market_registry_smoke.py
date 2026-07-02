import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_multi_market_registry import build_multi_market_adapter_registry
from btc_finance_platform.paper_multi_market_registry import build_multi_market_readiness_bundle
from btc_finance_platform.paper_multi_market_registry import build_multi_market_readiness_gate
from btc_finance_platform.paper_multi_market_registry import write_multi_market_readiness_bundle

if __name__ == "__main__":
    root = Path(ROOT)
    fixture = root / "fixtures" / "sample_multi_market_batch.json"
    output_dir = root / "artifacts" / "multi_market_readiness_bundle"
    registry = build_multi_market_adapter_registry()
    gate = build_multi_market_readiness_gate(fixture)
    bundle = build_multi_market_readiness_bundle(fixture)
    written = write_multi_market_readiness_bundle(fixture, output_dir)
    print(json.dumps({
        "registry": registry,
        "gate": gate,
        "bundle": {
            "ok": bundle["ok"],
            "type": bundle["type"],
            "source_file": bundle["source_file"],
            "paper_only": bundle["paper_only"],
            "operator_review_required": bundle["operator_review_required"],
        },
        "written": {
            "ok": written["ok"],
            "type": written["type"],
            "output_dir": written["output_dir"],
            "bundle_file": written["bundle_file"],
            "registry_file": written["registry_file"],
            "gate_file": written["gate_file"],
        },
    }, indent=2, sort_keys=True))
