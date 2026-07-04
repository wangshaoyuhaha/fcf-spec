import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_release_guard_handoff import build_p43_governance_release_guard_handoff
from btc_finance_platform.paper_governance_release_guard_handoff import build_p43_release_guard_boundary_handoff
from btc_finance_platform.paper_governance_release_guard_handoff import build_p43_release_guard_gate_handoff

def test_p43_release_guard_handoff_uses_baseline():
    result = build_p43_governance_release_guard_handoff()
    assert result["phase"] == "P43"
    assert result["step_range"] == "D7-D9"
    assert result["baseline_tests"] == 975
    assert result["release_guard_handoff_ready"] is True
    assert result["operator_review_required"] is True

def test_p43_release_guard_boundary_handoff_blocks_real_actions():
    result = build_p43_release_guard_boundary_handoff()
    assert result["operator_can_override_safety"] is False
    assert result["real_world_actions_allowed"] is False
    assert result["tag_allowed"] is False
    assert result["release_allowed"] is False
    assert result["deploy_allowed"] is False

def test_p43_release_guard_gate_handoff_blocks_release_deploy():
    result = build_p43_release_guard_gate_handoff()
    assert result["ready_for_p43_d10_d12"] is True
    assert result["ready_for_tag"] is False
    assert result["ready_for_release"] is False
    assert result["ready_for_deploy"] is False
