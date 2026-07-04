import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path: sys.path.insert(0, SRC)
from btc_finance_platform.paper_governance_operator_attestation_bridge import build_p40_governance_operator_attestation_bridge, build_p40_operator_attestation_boundary, build_p40_operator_attestation_readiness_gate
if __name__ == "__main__":
 result = {"bridge": build_p40_governance_operator_attestation_bridge(), "boundary": build_p40_operator_attestation_boundary(), "gate": build_p40_operator_attestation_readiness_gate()}
 print(json.dumps(result, indent=2, sort_keys=True))
