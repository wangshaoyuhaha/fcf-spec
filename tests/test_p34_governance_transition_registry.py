import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_transition_registry import build_p34_governance_transition_audit
from btc_finance_platform.paper_governance_transition_registry import build_p34_governance_transition_gate
from btc_finance_platform.paper_governance_transition_registry import build_p34_governance_transition_registry


def test_p34_governance_transition_registry_uses_861_baseline():
    result = build_p34_governance_transition_registry()
    assert result["phase"] == "P34"
    assert result["step_range"] == "D1-D3"
    assert result["baseline_tests"] == 861
    assert result["previous_phase"] == "P33"
    assert result["operator_review_required"] is True


def test_p34_governance_transition_audit_preserves_boundaries():
    result = build_p34_governance_transition_audit()
    assert result["passed"] is True
    assert result["p33_completion_preserved"] is True
    assert result["governance_boundary_preserved"] is True
    assert result["release_boundary_preserved"] is True
    assert result["real_world_actions_allowed"] is False


def test_p34_governance_transition_gate_blocks_release_deploy():
    result = build_p34_governance_transition_gate()
    assert result["ready_for_p34_work"] is True
    assert result["ready_for_tag"] is False
    assert result["ready_for_release"] is False
    assert result["ready_for_deploy"] is False
    assert result["operator_review_required"] is True
