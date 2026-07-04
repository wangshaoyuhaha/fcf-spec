import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_final_acceptance_lock_bridge import build_p45_governance_final_acceptance_lock_bridge
from btc_finance_platform.paper_governance_final_acceptance_lock_bridge import build_p45_final_acceptance_lock_boundary_bridge
from btc_finance_platform.paper_governance_final_acceptance_lock_bridge import build_p45_final_acceptance_lock_gate_bridge

def test_p45_final_acceptance_lock_bridge_uses_baseline():
    result = build_p45_governance_final_acceptance_lock_bridge()
    assert result["phase"] == "P45"
    assert result["step_range"] == "D1-D3"
    assert result["baseline_tests"] == 993
    assert result["final_acceptance_lock_bridge_ready"] is True
    assert result["final_acceptance_locked"] is True
    assert result["operator_review_required"] is True

def test_p45_final_acceptance_lock_boundary_bridge_blocks_real_actions():
    result = build_p45_final_acceptance_lock_boundary_bridge()
    assert result["final_acceptance_locked"] is True
    assert result["operator_can_override_safety"] is False
    assert result["real_world_actions_allowed"] is False
    assert result["tag_allowed"] is False
    assert result["release_allowed"] is False
    assert result["deploy_allowed"] is False

def test_p45_final_acceptance_lock_gate_bridge_blocks_release_deploy():
    result = build_p45_final_acceptance_lock_gate_bridge()
    assert result["ready_for_p45_d4_d6"] is True
    assert result["ready_for_tag"] is False
    assert result["ready_for_release"] is False
    assert result["ready_for_deploy"] is False
