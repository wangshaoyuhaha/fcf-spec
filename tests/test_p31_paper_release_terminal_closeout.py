import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_terminal_closeout import build_p31_terminal_packet
from btc_finance_platform.paper_release_terminal_closeout import build_p31_terminal_safety_gate
from btc_finance_platform.paper_release_terminal_closeout import build_p31_terminal_summary


def test_p31_terminal_packet_keeps_822_baseline():
    packet = build_p31_terminal_packet()
    assert packet["phase"] == "P31"
    assert packet["step_range"] == "D1-D3"
    assert packet["confirmed_previous_tests"] == 822
    assert packet["previous_phase"] == "P30-D4-D12"
    assert packet["operator_review_required"] is True


def test_p31_terminal_summary_blocks_deploy_and_real_actions():
    summary = build_p31_terminal_summary()
    assert summary["real_world_actions_allowed"] is False
    assert summary["deployment_allowed_now"] is False
    assert summary["operator_review_required"] is True


def test_p31_terminal_safety_gate_blocks_real_money_impact():
    gate = build_p31_terminal_safety_gate()
    assert gate["passed"] is True
    assert "real_exchange_api" in gate["blocked_actions"]
    assert "real_orders" in gate["blocked_actions"]
    assert "real_money_impact" in gate["blocked_actions"]
    assert gate["operator_review_required"] is True
