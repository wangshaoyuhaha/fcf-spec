import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_terminal_readiness import build_p31_terminal_completion_gate
from btc_finance_platform.paper_release_terminal_readiness import build_p31_terminal_readable_report
from btc_finance_platform.paper_release_terminal_readiness import build_p31_terminal_readiness_checklist


def test_p31_terminal_readable_report_uses_825_baseline():
    report = build_p31_terminal_readable_report()
    assert report["phase"] == "P31"
    assert report["step_range"] == "D4-D6"
    assert report["baseline_tests"] == 825
    assert report["operator_review_required"] is True


def test_p31_terminal_readiness_checklist_is_complete():
    checklist = build_p31_terminal_readiness_checklist()
    assert checklist["ready_for_completion_gate"] is True
    assert len(checklist["checklist"]) == 5
    assert all(item["passed"] for item in checklist["checklist"])


def test_p31_terminal_completion_gate_blocks_deploy():
    gate = build_p31_terminal_completion_gate()
    assert gate["passed"] is True
    assert gate["deployment_allowed_now"] is False
    assert gate["real_world_actions_allowed"] is False
    assert gate["operator_review_required"] is True
