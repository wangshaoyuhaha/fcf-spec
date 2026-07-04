import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_operator_review import build_p31_next_phase_gate
from btc_finance_platform.paper_release_operator_review import build_p31_no_release_guard
from btc_finance_platform.paper_release_operator_review import build_p31_operator_review_packet


def test_p31_operator_review_packet_uses_834_baseline():
    packet = build_p31_operator_review_packet()
    assert packet["phase"] == "P31"
    assert packet["baseline_tests"] == 834
    assert packet["status"] == "ready_for_operator_review"
    assert packet["operator_review_required"] is True


def test_p31_no_release_guard_blocks_automation():
    guard = build_p31_no_release_guard()
    assert guard["auto_tag_allowed"] is False
    assert guard["auto_release_allowed"] is False
    assert guard["auto_deploy_allowed"] is False
    assert guard["real_world_actions_allowed"] is False


def test_p31_next_phase_gate_requires_operator_review():
    gate = build_p31_next_phase_gate()
    assert gate["p31_completed"] is True
    assert gate["p32_allowed_without_operator_review"] is False
    assert gate["tag_allowed_without_operator_review"] is False
    assert gate["release_allowed_without_operator_review"] is False
    assert gate["operator_review_required"] is True
