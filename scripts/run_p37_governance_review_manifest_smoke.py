import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path: sys.path.insert(0, SRC)
from btc_finance_platform.paper_governance_review_manifest import build_p37_governance_review_manifest, build_p37_review_checkpoint, build_p37_review_manifest_gate
if __name__ == "__main__":
 result = {"manifest": build_p37_governance_review_manifest(), "checkpoint": build_p37_review_checkpoint(), "gate": build_p37_review_manifest_gate()}
 print(json.dumps(result, indent=2, sort_keys=True))
