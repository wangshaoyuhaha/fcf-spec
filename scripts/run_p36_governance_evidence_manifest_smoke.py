import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
 sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_evidence_manifest import build_p36_evidence_checkpoint
from btc_finance_platform.paper_governance_evidence_manifest import build_p36_evidence_manifest_gate
from btc_finance_platform.paper_governance_evidence_manifest import build_p36_governance_evidence_manifest


if __name__ == "__main__":
 result = {
  "governance_evidence_manifest": build_p36_governance_evidence_manifest(),
  "evidence_checkpoint": build_p36_evidence_checkpoint(),
  "evidence_manifest_gate": build_p36_evidence_manifest_gate(),
 }
 print(json.dumps(result, indent=2, sort_keys=True))
