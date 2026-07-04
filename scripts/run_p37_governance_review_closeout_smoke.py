import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path: sys.path.insert(0, SRC)
from btc_finance_platform.paper_governance_review_closeout import build_p37_governance_review_closeout, build_p37_review_final_packet, build_p37_review_completion_gate
if __name__ == "__main__":
 result = {"closeout": build_p37_governance_review_closeout(), "final_packet": build_p37_review_final_packet(), "gate": build_p37_review_completion_gate()}
 print(json.dumps(result, indent=2, sort_keys=True))
