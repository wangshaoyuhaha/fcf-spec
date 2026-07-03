import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_master_index import build_paper_release_master_index_closeout_checkpoint
from btc_finance_platform.paper_release_master_index import build_paper_release_master_index_export_packet
from btc_finance_platform.paper_release_master_index import build_paper_release_master_index_handoff_packet


def test_p24_d7_master_index_export_packet_is_local_static_read_only():
    packet = build_paper_release_master_index_export_packet()
    assert packet["ok"] is True
    assert packet["export_mode"] == "LOCAL_STATIC_READ_ONLY"
    assert packet["completion_gate"]["status"] == "PASSED"
    assert packet["deploy_enabled"] is False
    assert packet["real_trading_enabled"] is False


def test_p24_d8_master_index_closeout_checkpoint_passes_completion_and_safety_gates():
    closeout = build_paper_release_master_index_closeout_checkpoint()
    assert closeout["ok"] is True
    assert closeout["completion_gate_status"] == "PASSED"
    assert closeout["safety_gate_status"] == "PASSED"
    assert closeout["entry_count"] == 10
    assert closeout["operator_review_required"] is True


def test_p24_d9_master_index_handoff_packet_ready_for_index_archive():
    handoff = build_paper_release_master_index_handoff_packet()
    assert handoff["ok"] is True
    assert handoff["handoff_status"] == "READY_FOR_INDEX_ARCHIVE"
    assert handoff["next_phase_candidate"] == "P25 Paper Release Final Archive"
    assert handoff["deploy_enabled"] is False
    assert handoff["real_trading_enabled"] is False
