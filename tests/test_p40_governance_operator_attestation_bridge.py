import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path: sys.path.insert(0, SRC)
from btc_finance_platform.paper_governance_operator_attestation_bridge import build_p40_governance_operator_attestation_bridge, build_p40_operator_attestation_boundary, build_p40_operator_attestation_readiness_gate

def test_p40_governance_operator_attestation_bridge_uses_933_baseline():
 result = build_p40_governance_operator_attestation_bridge()
 assert result["phase"] == "P40"
 assert result["step_range"] == "D1-D3"
 assert result["baseline_tests"] == 933
 assert result["operator_attestation_bridge_ready"] is True
 assert result["operator_review_required"] is True

def test_p40_operator_attestation_boundary_blocks_real_actions():
 result = build_p40_operator_attestation_boundary()
 assert result["attestation_required"] is True
 assert result["operator_can_override_safety"] is False
 assert result["real_world_actions_allowed"] is False
 assert result["tag_allowed"] is False
 assert result["release_allowed"] is False
 assert result["deploy_allowed"] is False

def test_p40_operator_attestation_readiness_gate_blocks_release_deploy():
 result = build_p40_operator_attestation_readiness_gate()
 assert result["ready_for_p40_d4_d6"] is True
 assert result["ready_for_tag"] is False
 assert result["ready_for_release"] is False
 assert result["ready_for_deploy"] is False
