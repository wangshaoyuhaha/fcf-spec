import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_final_delivery import build_paper_release_final_delivery_packet
from btc_finance_platform.paper_release_final_delivery import evaluate_paper_release_final_delivery_safety
from btc_finance_platform.paper_release_final_delivery import summarize_paper_release_final_delivery


def test_p30_d1_final_delivery_packet_covers_p14_to_p29():
    packet = build_paper_release_final_delivery_packet()
    assert packet["ok"] is True
    assert packet["release_tag"] == "v14-learning-engine-paper"
    assert packet["delivery_item_count"] == 16
    assert packet["source_handoff_status"] == "READY_FOR_OPERATOR_RECEIPT_ARCHIVE"
    assert packet["real_trading_enabled"] is False


def test_p30_d2_final_delivery_summary_confirms_all_items_delivered():
    summary = summarize_paper_release_final_delivery()
    assert summary["ok"] is True
    assert summary["delivery_item_count"] == 16
    assert summary["delivered_count"] == 16
    assert summary["latest_phase"] == "P29"
    assert summary["read_only"] is True


def test_p30_d3_final_delivery_safety_gate_passes_no_deploy_boundary():
    gate = evaluate_paper_release_final_delivery_safety()
    assert gate["ok"] is True
    assert gate["status"] == "PASSED"
    assert gate["delivery_item_count"] == 16
    assert gate["deploy_enabled"] is False
    assert gate["real_money_impact"] is False
