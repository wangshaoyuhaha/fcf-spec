import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path: sys.path.insert(0, SRC)
from btc_finance_platform.paper_governance_compliance_dossier_handoff import build_p41_governance_compliance_dossier_handoff, build_p41_compliance_dossier_operator_packet, build_p41_compliance_dossier_next_gate
if __name__ == "__main__":
 result = {"handoff": build_p41_governance_compliance_dossier_handoff(), "packet": build_p41_compliance_dossier_operator_packet(), "gate": build_p41_compliance_dossier_next_gate()}
 print(json.dumps(result, indent=2, sort_keys=True))
