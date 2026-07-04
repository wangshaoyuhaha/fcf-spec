import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_phase_transition_acceptance import build_p33_transition_acceptance_lock
from btc_finance_platform.paper_phase_transition_acceptance import build_p33_transition_acceptance_packet
from btc_finance_platform.paper_phase_transition_acceptance import build_p33_transition_completion_receipt


def test_p33_transition_acceptance_packet_uses_858_baseline():
    result = build_p33_transition_acceptance_packet()
    assert result["phase"] == "P33"
    assert result["step_range"] == "D10-D12"
    assert result["baseline_tests"] == 858
    assert result["operator_review_required"] is True


def test_p33_transition_acceptance_lock_blocks_automation():
    result = build_p33_transition_acceptance_lock()
    assert result["locked"] is True
    assert result["auto_tag_allowed"] is False
    assert result["auto_release_allowed"] is False
    assert result["auto_deploy_allowed"] is False
    assert result["real_trading_allowed"] is False


def test_p33_transition_completion_receipt_blocks_release_deploy():
    result = build_p33_transition_completion_receipt()
    assert result["safe_to_close_phase"] is True
    assert result["ready_for_release"] is False
    assert result["ready_for_deploy"] is False
    assert result["real_world_actions_allowed"] is False
    assert result["operator_review_required"] is True
