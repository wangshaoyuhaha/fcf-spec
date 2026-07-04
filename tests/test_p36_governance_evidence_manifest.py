import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
 sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_evidence_manifest import build_p36_evidence_checkpoint
from btc_finance_platform.paper_governance_evidence_manifest import build_p36_evidence_manifest_gate
from btc_finance_platform.paper_governance_evidence_manifest import build_p36_governance_evidence_manifest


def test_p36_governance_evidence_manifest_uses_888_baseline():
 result = build_p36_governance_evidence_manifest()
 assert result["phase"] == "P36"
 assert result["step_range"] == "D4-D6"
 assert result["baseline_tests"] == 888
 assert result["previous_step"] == "P36-D1-D3"
 assert result["evidence_manifest_ready"] is True
 assert result["operator_review_required"] is True


def test_p36_evidence_checkpoint_preserves_integrity_boundary():
 result = build_p36_evidence_checkpoint()
 assert result["ledger_preserved"] is True
 assert result["integrity_boundary_preserved"] is True
 assert result["evidence_mutable"] is False
 assert result["real_world_actions_allowed"] is False
 assert result["operator_review_required"] is True


def test_p36_evidence_manifest_gate_blocks_release_deploy():
 result = build_p36_evidence_manifest_gate()
 assert result["ready_for_p36_d7_d9"] is True
 assert result["ready_for_tag"] is False
 assert result["ready_for_release"] is False
 assert result["ready_for_deploy"] is False
 assert result["operator_review_required"] is True
