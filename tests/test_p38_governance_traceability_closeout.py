import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path: sys.path.insert(0, SRC)
from btc_finance_platform.paper_governance_traceability_closeout import build_p38_governance_traceability_closeout, build_p38_traceability_final_packet, build_p38_traceability_completion_gate

def test_p38_governance_traceability_closeout_uses_918_baseline():
 result = build_p38_governance_traceability_closeout()
 assert result["phase"] == "P38"
 assert result["step_range"] == "D10-D12"
 assert result["baseline_tests"] == 918
 assert result["traceability_closeout_ready"] is True
 assert result["operator_review_required"] is True

def test_p38_traceability_final_packet_preserves_artifacts():
 result = build_p38_traceability_final_packet()
 assert result["bridge_preserved"] is True
 assert result["manifest_preserved"] is True
 assert result["handoff_preserved"] is True
 assert result["trace_mutable"] is False
 assert result["real_world_actions_allowed"] is False

def test_p38_traceability_completion_gate_blocks_release_deploy():
 result = build_p38_traceability_completion_gate()
 assert result["p38_complete"] is True
 assert result["ready_for_next_phase"] is True
 assert result["ready_for_tag"] is False
 assert result["ready_for_release"] is False
 assert result["ready_for_deploy"] is False
