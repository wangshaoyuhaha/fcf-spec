import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_next_phase_continuity import build_p32_continuity_audit
from btc_finance_platform.paper_next_phase_continuity import build_p32_continuity_gate
from btc_finance_platform.paper_next_phase_continuity import build_p32_continuity_map


def test_p32_continuity_map_uses_840_baseline():
    result = build_p32_continuity_map()
    assert result["phase"] == "P32"
    assert result["step_range"] == "D4-D6"
    assert result["baseline_tests"] == 840
    assert result["operator_review_required"] is True


def test_p32_continuity_audit_preserves_boundaries():
    result = build_p32_continuity_audit()
    assert result["passed"] is True
    assert result["p31_boundary_preserved"] is True
    assert result["p32_entry_preserved"] is True
    assert result["release_boundary_preserved"] is True
    assert result["real_world_actions_allowed"] is False


def test_p32_continuity_gate_blocks_release_deploy():
    result = build_p32_continuity_gate()
    assert result["ready_for_next_p32_step"] is True
    assert result["ready_for_tag"] is False
    assert result["ready_for_release"] is False
    assert result["ready_for_deploy"] is False
    assert result["operator_review_required"] is True
