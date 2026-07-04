import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path: sys.path.insert(0, SRC)
from btc_finance_platform.paper_governance_review_manifest import build_p37_governance_review_manifest, build_p37_review_checkpoint, build_p37_review_manifest_gate

def test_p37_governance_review_manifest_uses_900_baseline():
 result = build_p37_governance_review_manifest()
 assert result["phase"] == "P37"
 assert result["step_range"] == "D4-D6"
 assert result["baseline_tests"] == 900
 assert result["review_manifest_ready"] is True
 assert result["operator_review_required"] is True

def test_p37_review_checkpoint_preserves_boundary():
 result = build_p37_review_checkpoint()
 assert result["bridge_preserved"] is True
 assert result["review_boundary_preserved"] is True
 assert result["real_world_actions_allowed"] is False
 assert result["operator_review_required"] is True

def test_p37_review_manifest_gate_blocks_release_deploy():
 result = build_p37_review_manifest_gate()
 assert result["ready_for_p37_d7_d9"] is True
 assert result["ready_for_tag"] is False
 assert result["ready_for_release"] is False
 assert result["ready_for_deploy"] is False
