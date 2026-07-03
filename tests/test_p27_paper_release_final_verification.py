import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_final_verification import build_paper_release_final_verification_packet
from btc_finance_platform.paper_release_final_verification import evaluate_paper_release_final_verification_safety
from btc_finance_platform.paper_release_final_verification import summarize_paper_release_final_verification


def test_p27_d1_final_verification_packet_covers_p14_to_p26():
    packet = build_paper_release_final_verification_packet()
    assert packet["ok"] is True
    assert packet["release_tag"] == "v14-learning-engine-paper"
    assert packet["verification_item_count"] == 13
    assert packet["source_handoff_status"] == "READY_FOR_RECEIPT_ARCHIVE"
    assert packet["real_trading_enabled"] is False


def test_p27_d2_final_verification_summary_confirms_all_items_verified():
    summary = summarize_paper_release_final_verification()
    assert summary["ok"] is True
    assert summary["verification_item_count"] == 13
    assert summary["verified_count"] == 13
    assert summary["latest_phase"] == "P26"
    assert summary["read_only"] is True


def test_p27_d3_final_verification_safety_gate_passes_no_deploy_boundary():
    gate = evaluate_paper_release_final_verification_safety()
    assert gate["ok"] is True
    assert gate["status"] == "PASSED"
    assert gate["verification_item_count"] == 13
    assert gate["deploy_enabled"] is False
    assert gate["real_money_impact"] is False
