import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path: sys.path.insert(0, SRC)
from btc_finance_platform.paper_governance_review_handoff import build_p37_governance_review_handoff, build_p37_review_operator_packet, build_p37_review_next_gate

def test_p37_governance_review_handoff_uses_903_baseline():
 result = build_p37_governance_review_handoff()
 assert result["phase"] == "P37"
 assert result["step_range"] == "D7-D9"
 assert result["baseline_tests"] == 903
 assert result["review_handoff_ready"] is True
 assert result["operator_review_required"] is True

def test_p37_review_operator_packet_blocks_real_actions():
 result = build_p37_review_operator_packet()
 assert result["manifest_preserved"] is True
 assert result["operator_can_override_safety"] is False
 assert result["real_world_actions_allowed"] is False
 assert result["tag_allowed"] is False
 assert result["release_allowed"] is False
 assert result["deploy_allowed"] is False

def test_p37_review_next_gate_blocks_release_deploy():
 result = build_p37_review_next_gate()
 assert result["ready_for_p37_d10_d12"] is True
 assert result["ready_for_tag"] is False
 assert result["ready_for_release"] is False
 assert result["ready_for_deploy"] is False
