import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.operator_evidence_navigation import build_operator_evidence_navigation_closeout_checkpoint
from btc_finance_platform.operator_evidence_navigation import build_operator_evidence_navigation_export_packet
from btc_finance_platform.operator_evidence_navigation import build_operator_evidence_navigation_readable_map


def test_p18_d7_navigation_readable_map_lists_all_routes():
    result = build_operator_evidence_navigation_readable_map()
    assert result["ok"] is True
    assert result["item_count"] == 7
    assert result["read_only"] is True
    assert result["deploy_enabled"] is False
    assert result["real_trading_enabled"] is False


def test_p18_d8_navigation_export_packet_is_local_static_read_only():
    packet = build_operator_evidence_navigation_export_packet()
    assert packet["ok"] is True
    assert packet["export_mode"] == "LOCAL_STATIC_READ_ONLY"
    assert packet["safety_gate"]["status"] == "PASSED"
    assert packet["deploy_enabled"] is False
    assert packet["real_trading_enabled"] is False


def test_p18_d9_navigation_closeout_checkpoint_sets_p19_boundary():
    checkpoint = build_operator_evidence_navigation_closeout_checkpoint()
    assert checkpoint["ok"] is True
    assert checkpoint["route_count"] == 7
    assert checkpoint["safety_gate_status"] == "PASSED"
    assert checkpoint["next_phase_candidate"] == "P19 Local Evidence Console Archive View"
    assert checkpoint["operator_review_required"] is True
