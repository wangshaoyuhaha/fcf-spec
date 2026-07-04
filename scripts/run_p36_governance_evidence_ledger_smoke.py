import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
 sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_evidence_ledger import build_p36_evidence_integrity_boundary
from btc_finance_platform.paper_governance_evidence_ledger import build_p36_evidence_readiness_gate
from btc_finance_platform.paper_governance_evidence_ledger import build_p36_governance_evidence_ledger


if __name__ == "__main__":
 result = {
  "governance_evidence_ledger": build_p36_governance_evidence_ledger(),
  "evidence_integrity_boundary": build_p36_evidence_integrity_boundary(),
  "evidence_readiness_gate": build_p36_evidence_readiness_gate(),
 }
 print(json.dumps(result, indent=2, sort_keys=True))
