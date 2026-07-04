import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
 sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_acceptance_closeout import build_p35_acceptance_completion_gate
from btc_finance_platform.paper_governance_acceptance_closeout import build_p35_acceptance_final_packet
from btc_finance_platform.paper_governance_acceptance_closeout import build_p35_governance_acceptance_closeout


def test_p35_governance_acceptance_closeout_uses_882_baseline():
 result = build_p35_governance_acceptance_closeout()
 assert result["phase"] == "P35"
 assert result["step_range"] == "D10-D12"
 assert result["baseline_tests"] == 882
 assert result["previous_step"] == "P35-D7-D9"
 assert result["acceptance_closeout_ready"] is True
 assert result["operator_review_required"] is True


def test_p35_acceptance_final_packet_preserves_artifacts():
 result = build_p35_acceptance_final_packet()
 assert result["bridge_preserved"] is True
 assert result["manifest_preserved"] is True
 assert result["handoff_preserved"] is True
 assert result["real_world_actions_allowed"] is False
 assert result["operator_review_required"] is True


def test_p35_acceptance_completion_gate_blocks_release_deploy():
 result = build_p35_acceptance_completion_gate()
 assert result["p35_complete"] is True
 assert result["ready_for_next_phase"] is True
 assert result["ready_for_tag"] is False
 assert result["ready_for_release"] is False
 assert result["ready_for_deploy"] is False
 assert result["operator_review_required"] is True
