import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path: sys.path.insert(0, SRC)
from btc_finance_platform.paper_governance_signoff_handoff import build_p42_governance_signoff_handoff, build_p42_signoff_operator_packet, build_p42_signoff_next_gate
if __name__ == "__main__":
 result = {"handoff": build_p42_governance_signoff_handoff(), "packet": build_p42_signoff_operator_packet(), "gate": build_p42_signoff_next_gate()}
 print(json.dumps(result, indent=2, sort_keys=True))
