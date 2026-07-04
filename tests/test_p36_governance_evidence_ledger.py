import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
 sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_evidence_ledger import build_p36_evidence_integrity_boundary
from btc_finance_platform.paper_governance_evidence_ledger import build_p36_evidence_readiness_gate
from btc_finance_platform.paper_governance_evidence_ledger import build_p36_governance_evidence_ledger


def test_p36_governance_evidence_ledger_uses_885_baseline():
 result = build_p36_governance_evidence_ledger()
 assert result["phase"] == "P36"
 assert result["step_range"] == "D1-D3"
 assert result["baseline_tests"] == 885
 assert result["previous_phase"] == "P35"
 assert result["evidence_ledger_ready"] is True
 assert result["operator_review_required"] is True


def test_p36_evidence_integrity_boundary_blocks_mutation_and_real_actions():
 result = build_p36_evidence_integrity_boundary()
 assert result["evidence_mutable"] is False
 assert result["operator_review_required"] is True
 assert result["operator_can_override_safety"] is False
 assert result["real_world_actions_allowed"] is False
 assert result["tag_allowed"] is False
 assert result["release_allowed"] is False
 assert result["deploy_allowed"] is False


def test_p36_evidence_readiness_gate_blocks_release_deploy():
 result = build_p36_evidence_readiness_gate()
 assert result["ready_for_p36_d4_d6"] is True
 assert result["ready_for_tag"] is False
 assert result["ready_for_release"] is False
 assert result["ready_for_deploy"] is False
 assert result["operator_review_required"] is True
