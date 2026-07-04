import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path: sys.path.insert(0, SRC)
from btc_finance_platform.paper_governance_operator_attestation_manifest import build_p40_governance_operator_attestation_manifest, build_p40_operator_attestation_checkpoint, build_p40_operator_attestation_manifest_gate
if __name__ == "__main__":
 result = {"manifest": build_p40_governance_operator_attestation_manifest(), "checkpoint": build_p40_operator_attestation_checkpoint(), "gate": build_p40_operator_attestation_manifest_gate()}
 print(json.dumps(result, indent=2, sort_keys=True))
