import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path: sys.path.insert(0, SRC)
from btc_finance_platform.paper_governance_review_closeout import build_p37_governance_review_closeout, build_p37_review_final_packet, build_p37_review_completion_gate

def test_p37_governance_review_closeout_uses_906_baseline():
 result = build_p37_governance_review_closeout()
 assert result["phase"] == "P37"
 assert result["step_range"] == "D10-D12"
 assert result["baseline_tests"] == 906
 assert result["review_closeout_ready"] is True
 assert result["operator_review_required"] is True

def test_p37_review_final_packet_preserves_artifacts():
 result = build_p37_review_final_packet()
 assert result["bridge_preserved"] is True
 assert result["manifest_preserved"] is True
 assert result["handoff_preserved"] is True
 assert result["real_world_actions_allowed"] is False
 assert result["operator_review_required"] is True

def test_p37_review_completion_gate_blocks_release_deploy():
 result = build_p37_review_completion_gate()
 assert result["p37_complete"] is True
 assert result["ready_for_next_phase"] is True
 assert result["ready_for_tag"] is False
 assert result["ready_for_release"] is False
 assert result["ready_for_deploy"] is False
