import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_release_guard_closeout import build_p43_governance_release_guard_closeout
from btc_finance_platform.paper_governance_release_guard_closeout import build_p43_release_guard_boundary_closeout
from btc_finance_platform.paper_governance_release_guard_closeout import build_p43_release_guard_gate_closeout

def test_p43_release_guard_closeout_uses_baseline():
    result = build_p43_governance_release_guard_closeout()
    assert result["phase"] == "P43"
    assert result["step_range"] == "D10-D12"
    assert result["baseline_tests"] == 978
    assert result["release_guard_closeout_ready"] is True
    assert result["operator_review_required"] is True

def test_p43_release_guard_boundary_closeout_blocks_real_actions():
    result = build_p43_release_guard_boundary_closeout()
    assert result["operator_can_override_safety"] is False
    assert result["real_world_actions_allowed"] is False
    assert result["tag_allowed"] is False
    assert result["release_allowed"] is False
    assert result["deploy_allowed"] is False

def test_p43_release_guard_gate_closeout_blocks_release_deploy():
    result = build_p43_release_guard_gate_closeout()
    assert result["ready_for_next_phase"] is True
    assert result["ready_for_tag"] is False
    assert result["ready_for_release"] is False
    assert result["ready_for_deploy"] is False
