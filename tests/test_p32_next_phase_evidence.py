import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_next_phase_evidence import build_p32_evidence_audit_trail
from btc_finance_platform.paper_next_phase_evidence import build_p32_evidence_gate
from btc_finance_platform.paper_next_phase_evidence import build_p32_evidence_index


def test_p32_evidence_index_uses_843_baseline():
    result = build_p32_evidence_index()
    assert result["phase"] == "P32"
    assert result["step_range"] == "D7-D9"
    assert result["baseline_tests"] == 843
    assert result["operator_review_required"] is True


def test_p32_evidence_audit_trail_preserves_boundaries():
    result = build_p32_evidence_audit_trail()
    assert result["passed"] is True
    assert result["previous_phase_preserved"] is True
    assert result["continuity_preserved"] is True
    assert result["release_boundary_preserved"] is True
    assert result["real_world_actions_allowed"] is False


def test_p32_evidence_gate_blocks_release_deploy():
    result = build_p32_evidence_gate()
    assert result["ready_for_next_p32_step"] is True
    assert result["ready_for_release"] is False
    assert result["ready_for_deploy"] is False
    assert result["operator_review_required"] is True
