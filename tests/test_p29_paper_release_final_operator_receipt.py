import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_final_operator_receipt import build_paper_release_final_operator_receipt
from btc_finance_platform.paper_release_final_operator_receipt import evaluate_paper_release_final_operator_receipt_safety
from btc_finance_platform.paper_release_final_operator_receipt import summarize_paper_release_final_operator_receipt


def test_p29_d1_final_operator_receipt_covers_p14_to_p28():
    receipt = build_paper_release_final_operator_receipt()
    assert receipt["ok"] is True
    assert receipt["release_tag"] == "v14-learning-engine-paper"
    assert receipt["receipt_item_count"] == 15
    assert receipt["source_handoff_status"] == "READY_FOR_SEAL_ARCHIVE"
    assert receipt["real_trading_enabled"] is False


def test_p29_d2_final_operator_receipt_summary_confirms_all_items_receipted():
    summary = summarize_paper_release_final_operator_receipt()
    assert summary["ok"] is True
    assert summary["receipt_item_count"] == 15
    assert summary["receipted_count"] == 15
    assert summary["latest_phase"] == "P28"
    assert summary["read_only"] is True


def test_p29_d3_final_operator_receipt_safety_gate_passes_no_deploy_boundary():
    gate = evaluate_paper_release_final_operator_receipt_safety()
    assert gate["ok"] is True
    assert gate["status"] == "PASSED"
    assert gate["receipt_item_count"] == 15
    assert gate["deploy_enabled"] is False
    assert gate["real_money_impact"] is False
