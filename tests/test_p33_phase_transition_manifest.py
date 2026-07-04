import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_phase_transition_manifest import build_p33_manifest_gate
from btc_finance_platform.paper_phase_transition_manifest import build_p33_transition_checkpoint
from btc_finance_platform.paper_phase_transition_manifest import build_p33_transition_manifest


def test_p33_transition_manifest_uses_852_baseline():
    result = build_p33_transition_manifest()
    assert result["phase"] == "P33"
    assert result["step_range"] == "D4-D6"
    assert result["baseline_tests"] == 852
    assert result["operator_review_required"] is True


def test_p33_transition_checkpoint_preserves_registry():
    result = build_p33_transition_checkpoint()
    assert result["passed"] is True
    assert result["baseline_tests"] == 852
    assert result["transition_registry_preserved"] is True
    assert result["release_boundary_preserved"] is True
    assert result["real_world_actions_allowed"] is False


def test_p33_manifest_gate_blocks_release_deploy():
    result = build_p33_manifest_gate()
    assert result["ready_for_next_p33_step"] is True
    assert result["ready_for_tag"] is False
    assert result["ready_for_release"] is False
    assert result["ready_for_deploy"] is False
    assert result["operator_review_required"] is True
