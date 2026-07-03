import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_evidence_snapshot import build_paper_release_evidence_snapshot_closeout_checkpoint
from btc_finance_platform.paper_release_evidence_snapshot import build_paper_release_evidence_snapshot_export_packet
from btc_finance_platform.paper_release_evidence_snapshot import build_paper_release_evidence_snapshot_handoff_packet


def test_p23_d7_snapshot_export_packet_is_local_static_read_only():
    packet = build_paper_release_evidence_snapshot_export_packet()
    assert packet["ok"] is True
    assert packet["export_mode"] == "LOCAL_STATIC_READ_ONLY"
    assert packet["completion_gate"]["status"] == "PASSED"
    assert packet["deploy_enabled"] is False
    assert packet["real_trading_enabled"] is False


def test_p23_d8_snapshot_closeout_checkpoint_passes_completion_and_safety_gates():
    closeout = build_paper_release_evidence_snapshot_closeout_checkpoint()
    assert closeout["ok"] is True
    assert closeout["completion_gate_status"] == "PASSED"
    assert closeout["safety_gate_status"] == "PASSED"
    assert closeout["item_count"] == 9
    assert closeout["operator_review_required"] is True


def test_p23_d9_snapshot_handoff_packet_ready_for_snapshot_archive():
    handoff = build_paper_release_evidence_snapshot_handoff_packet()
    assert handoff["ok"] is True
    assert handoff["handoff_status"] == "READY_FOR_SNAPSHOT_ARCHIVE"
    assert handoff["next_phase_candidate"] == "P24 Paper Release Master Index"
    assert handoff["deploy_enabled"] is False
    assert handoff["real_trading_enabled"] is False
