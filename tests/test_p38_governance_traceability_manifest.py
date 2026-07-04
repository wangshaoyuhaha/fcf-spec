import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path: sys.path.insert(0, SRC)
from btc_finance_platform.paper_governance_traceability_manifest import build_p38_governance_traceability_manifest, build_p38_traceability_checkpoint, build_p38_traceability_manifest_gate

def test_p38_governance_traceability_manifest_uses_912_baseline():
 result = build_p38_governance_traceability_manifest()
 assert result["phase"] == "P38"
 assert result["step_range"] == "D4-D6"
 assert result["baseline_tests"] == 912
 assert result["traceability_manifest_ready"] is True
 assert result["operator_review_required"] is True

def test_p38_traceability_checkpoint_preserves_boundary():
 result = build_p38_traceability_checkpoint()
 assert result["bridge_preserved"] is True
 assert result["traceability_boundary_preserved"] is True
 assert result["trace_mutable"] is False
 assert result["real_world_actions_allowed"] is False

def test_p38_traceability_manifest_gate_blocks_release_deploy():
 result = build_p38_traceability_manifest_gate()
 assert result["ready_for_p38_d7_d9"] is True
 assert result["ready_for_tag"] is False
 assert result["ready_for_release"] is False
 assert result["ready_for_deploy"] is False
