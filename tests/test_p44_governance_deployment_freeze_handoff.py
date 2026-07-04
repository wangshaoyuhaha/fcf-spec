import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_deployment_freeze_handoff import build_p44_governance_deployment_freeze_handoff
from btc_finance_platform.paper_governance_deployment_freeze_handoff import build_p44_deployment_freeze_boundary_handoff
from btc_finance_platform.paper_governance_deployment_freeze_handoff import build_p44_deployment_freeze_gate_handoff

def test_p44_deployment_freeze_handoff_uses_baseline():
    result = build_p44_governance_deployment_freeze_handoff()
    assert result["phase"] == "P44"
    assert result["step_range"] == "D7-D9"
    assert result["baseline_tests"] == 987
    assert result["deployment_freeze_handoff_ready"] is True
    assert result["operator_review_required"] is True

def test_p44_deployment_freeze_boundary_handoff_blocks_real_actions():
    result = build_p44_deployment_freeze_boundary_handoff()
    assert result["deployment_frozen"] is True
    assert result["operator_can_override_safety"] is False
    assert result["real_world_actions_allowed"] is False
    assert result["tag_allowed"] is False
    assert result["release_allowed"] is False
    assert result["deploy_allowed"] is False

def test_p44_deployment_freeze_gate_handoff_blocks_release_deploy():
    result = build_p44_deployment_freeze_gate_handoff()
    assert result["ready_for_p44_d10_d12"] is True
    assert result["ready_for_tag"] is False
    assert result["ready_for_release"] is False
    assert result["ready_for_deploy"] is False
