import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path: sys.path.insert(0, SRC)
from btc_finance_platform.paper_governance_signoff_closeout import build_p42_governance_signoff_closeout, build_p42_signoff_final_packet, build_p42_signoff_completion_gate
if __name__ == "__main__":
 result = {"closeout": build_p42_governance_signoff_closeout(), "final_packet": build_p42_signoff_final_packet(), "gate": build_p42_signoff_completion_gate()}
 print(json.dumps(result, indent=2, sort_keys=True))
