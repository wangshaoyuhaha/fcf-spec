import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_phase_transition_evidence import build_p33_evidence_gate
from btc_finance_platform.paper_phase_transition_evidence import build_p33_transition_evidence_audit
from btc_finance_platform.paper_phase_transition_evidence import build_p33_transition_evidence_index


def test_p33_transition_evidence_index_uses_855_baseline():
    result = build_p33_transition_evidence_index()
    assert result["phase"] == "P33"
    assert result["step_range"] == "D7-D9"
    assert result["baseline_tests"] == 855
    assert result["operator_review_required"] is True


def test_p33_transition_evidence_audit_preserves_manifest():
    result = build_p33_transition_evidence_audit()
    assert result["passed"] is True
    assert result["manifest_preserved"] is True
    assert result["checkpoint_preserved"] is True
    assert result["release_boundary_preserved"] is True
    assert result["real_world_actions_allowed"] is False


def test_p33_evidence_gate_blocks_release_deploy():
    result = build_p33_evidence_gate()
    assert result["ready_for_next_p33_step"] is True
    assert result["ready_for_tag"] is False
    assert result["ready_for_release"] is False
    assert result["ready_for_deploy"] is False
    assert result["operator_review_required"] is True
