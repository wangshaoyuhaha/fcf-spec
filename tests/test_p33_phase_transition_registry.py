import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_phase_transition_registry import build_p33_transition_audit
from btc_finance_platform.paper_phase_transition_registry import build_p33_transition_gate
from btc_finance_platform.paper_phase_transition_registry import build_p33_transition_registry


def test_p33_transition_registry_uses_849_baseline():
    result = build_p33_transition_registry()
    assert result["phase"] == "P33"
    assert result["step_range"] == "D1-D3"
    assert result["baseline_tests"] == 849
    assert result["previous_phase"] == "P32"
    assert result["operator_review_required"] is True


def test_p33_transition_audit_preserves_boundaries():
    result = build_p33_transition_audit()
    assert result["passed"] is True
    assert result["p32_completion_preserved"] is True
    assert result["release_boundary_preserved"] is True
    assert result["deploy_boundary_preserved"] is True
    assert result["real_world_actions_allowed"] is False


def test_p33_transition_gate_blocks_release_deploy():
    result = build_p33_transition_gate()
    assert result["ready_for_p33_work"] is True
    assert result["ready_for_tag"] is False
    assert result["ready_for_release"] is False
    assert result["ready_for_deploy"] is False
    assert result["operator_review_required"] is True
