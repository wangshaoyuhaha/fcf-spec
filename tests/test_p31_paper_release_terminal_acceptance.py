import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_terminal_acceptance import build_p31_terminal_acceptance_packet
from btc_finance_platform.paper_release_terminal_acceptance import build_p31_terminal_completion_receipt
from btc_finance_platform.paper_release_terminal_acceptance import build_p31_terminal_release_lock


def test_p31_terminal_acceptance_packet_uses_831_baseline():
    packet = build_p31_terminal_acceptance_packet()
    assert packet["phase"] == "P31"
    assert packet["step_range"] == "D10-D12"
    assert packet["baseline_tests"] == 831
    assert packet["operator_review_required"] is True


def test_p31_terminal_release_lock_blocks_auto_release():
    lock = build_p31_terminal_release_lock()
    assert lock["locked"] is True
    assert lock["auto_tag_allowed"] is False
    assert lock["auto_release_allowed"] is False
    assert lock["auto_deploy_allowed"] is False
    assert lock["real_trading_allowed"] is False


def test_p31_terminal_completion_receipt_blocks_real_world_actions():
    receipt = build_p31_terminal_completion_receipt()
    assert receipt["safe_to_close_phase"] is True
    assert receipt["deployment_allowed_now"] is False
    assert receipt["real_world_actions_allowed"] is False
    assert receipt["operator_review_required"] is True
