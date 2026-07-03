import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.operator_evidence_archive_view import build_operator_evidence_archive_closeout_checkpoint
from btc_finance_platform.operator_evidence_archive_view import build_operator_evidence_archive_export_packet
from btc_finance_platform.operator_evidence_archive_view import build_operator_evidence_archive_readable_map


def test_p19_d7_archive_readable_map_lists_all_archives():
    result = build_operator_evidence_archive_readable_map()
    assert result["ok"] is True
    assert result["item_count"] == 5
    assert result["timeline_count"] == 5
    assert result["read_only"] is True
    assert result["deploy_enabled"] is False


def test_p19_d8_archive_export_packet_is_local_static_read_only():
    packet = build_operator_evidence_archive_export_packet()
    assert packet["ok"] is True
    assert packet["export_mode"] == "LOCAL_STATIC_READ_ONLY"
    assert packet["safety_gate"]["status"] == "PASSED"
    assert packet["deploy_enabled"] is False
    assert packet["real_trading_enabled"] is False


def test_p19_d9_archive_closeout_checkpoint_sets_p20_boundary():
    checkpoint = build_operator_evidence_archive_closeout_checkpoint()
    assert checkpoint["ok"] is True
    assert checkpoint["archive_count"] == 5
    assert checkpoint["safety_gate_status"] == "PASSED"
    assert checkpoint["next_phase_candidate"] == "P20 Local Evidence Console Final Review"
    assert checkpoint["operator_review_required"] is True
