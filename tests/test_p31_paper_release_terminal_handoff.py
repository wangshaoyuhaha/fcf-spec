import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_terminal_handoff import build_p31_terminal_checkpoint
from btc_finance_platform.paper_release_terminal_handoff import build_p31_terminal_export_packet
from btc_finance_platform.paper_release_terminal_handoff import build_p31_terminal_handoff_packet


def test_p31_terminal_export_packet_uses_828_baseline():
    packet = build_p31_terminal_export_packet()
    assert packet["phase"] == "P31"
    assert packet["step_range"] == "D7-D9"
    assert packet["baseline_tests"] == 828
    assert packet["export_ready"] is True
    assert packet["operator_review_required"] is True


def test_p31_terminal_checkpoint_blocks_release_actions():
    checkpoint = build_p31_terminal_checkpoint()
    assert checkpoint["previous_tests"] == 828
    assert checkpoint["deploy_allowed_now"] is False
    assert checkpoint["real_world_actions_allowed"] is False


def test_p31_terminal_handoff_requires_operator_review():
    handoff = build_p31_terminal_handoff_packet()
    assert handoff["safe_to_continue"] is True
    assert handoff["auto_release_allowed"] is False
    assert handoff["auto_deploy_allowed"] is False
    assert handoff["real_trading_allowed"] is False
    assert handoff["operator_review_required"] is True
