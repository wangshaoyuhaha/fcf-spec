import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_final_archive import build_paper_release_final_archive_packet
from btc_finance_platform.paper_release_final_archive import evaluate_paper_release_final_archive_safety
from btc_finance_platform.paper_release_final_archive import summarize_paper_release_final_archive


def test_p25_d1_final_archive_packet_covers_p14_to_p24():
    packet = build_paper_release_final_archive_packet()
    assert packet["ok"] is True
    assert packet["release_tag"] == "v14-learning-engine-paper"
    assert packet["archive_item_count"] == 11
    assert packet["source_handoff_status"] == "READY_FOR_INDEX_ARCHIVE"
    assert packet["real_trading_enabled"] is False


def test_p25_d2_final_archive_summary_confirms_all_items_archived():
    summary = summarize_paper_release_final_archive()
    assert summary["ok"] is True
    assert summary["archive_item_count"] == 11
    assert summary["archived_count"] == 11
    assert summary["latest_phase"] == "P24"
    assert summary["read_only"] is True


def test_p25_d3_final_archive_safety_gate_passes_no_deploy_boundary():
    gate = evaluate_paper_release_final_archive_safety()
    assert gate["ok"] is True
    assert gate["status"] == "PASSED"
    assert gate["archive_item_count"] == 11
    assert gate["deploy_enabled"] is False
    assert gate["real_money_impact"] is False
