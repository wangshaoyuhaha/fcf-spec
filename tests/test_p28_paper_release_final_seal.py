import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_final_seal import build_paper_release_final_seal_packet
from btc_finance_platform.paper_release_final_seal import evaluate_paper_release_final_seal_safety
from btc_finance_platform.paper_release_final_seal import summarize_paper_release_final_seal


def test_p28_d1_final_seal_packet_covers_p14_to_p27():
    packet = build_paper_release_final_seal_packet()
    assert packet["ok"] is True
    assert packet["release_tag"] == "v14-learning-engine-paper"
    assert packet["seal_item_count"] == 14
    assert packet["source_handoff_status"] == "READY_FOR_VERIFICATION_ARCHIVE"
    assert packet["real_trading_enabled"] is False


def test_p28_d2_final_seal_summary_confirms_all_items_sealed():
    summary = summarize_paper_release_final_seal()
    assert summary["ok"] is True
    assert summary["seal_item_count"] == 14
    assert summary["sealed_count"] == 14
    assert summary["latest_phase"] == "P27"
    assert summary["read_only"] is True


def test_p28_d3_final_seal_safety_gate_passes_no_deploy_boundary():
    gate = evaluate_paper_release_final_seal_safety()
    assert gate["ok"] is True
    assert gate["status"] == "PASSED"
    assert gate["seal_item_count"] == 14
    assert gate["deploy_enabled"] is False
    assert gate["real_money_impact"] is False
