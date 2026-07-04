import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path: sys.path.insert(0, SRC)
from btc_finance_platform.paper_governance_audit_trail_bridge import build_p39_governance_audit_trail_bridge, build_p39_audit_trail_boundary, build_p39_audit_trail_readiness_gate

def test_p39_governance_audit_trail_bridge_uses_921_baseline():
 result = build_p39_governance_audit_trail_bridge()
 assert result["phase"] == "P39"
 assert result["step_range"] == "D1-D3"
 assert result["baseline_tests"] == 921
 assert result["audit_trail_bridge_ready"] is True
 assert result["operator_review_required"] is True

def test_p39_audit_trail_boundary_blocks_mutation_and_real_actions():
 result = build_p39_audit_trail_boundary()
 assert result["audit_trail_mutable"] is False
 assert result["operator_can_override_safety"] is False
 assert result["real_world_actions_allowed"] is False
 assert result["tag_allowed"] is False
 assert result["release_allowed"] is False
 assert result["deploy_allowed"] is False

def test_p39_audit_trail_readiness_gate_blocks_release_deploy():
 result = build_p39_audit_trail_readiness_gate()
 assert result["ready_for_p39_d4_d6"] is True
 assert result["ready_for_tag"] is False
 assert result["ready_for_release"] is False
 assert result["ready_for_deploy"] is False
