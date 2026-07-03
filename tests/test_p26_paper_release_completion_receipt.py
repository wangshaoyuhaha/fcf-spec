import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_completion_receipt import build_paper_release_completion_receipt
from btc_finance_platform.paper_release_completion_receipt import evaluate_paper_release_completion_receipt_safety
from btc_finance_platform.paper_release_completion_receipt import summarize_paper_release_completion_receipt


def test_p26_d1_completion_receipt_covers_p14_to_p25():
    receipt = build_paper_release_completion_receipt()
    assert receipt["ok"] is True
    assert receipt["release_tag"] == "v14-learning-engine-paper"
    assert receipt["receipt_item_count"] == 12
    assert receipt["source_handoff_status"] == "READY_FOR_FINAL_ARCHIVE_CLOSEOUT"
    assert receipt["real_trading_enabled"] is False


def test_p26_d2_completion_receipt_summary_confirms_all_items_receipted():
    summary = summarize_paper_release_completion_receipt()
    assert summary["ok"] is True
    assert summary["receipt_item_count"] == 12
    assert summary["receipted_count"] == 12
    assert summary["latest_phase"] == "P25"
    assert summary["read_only"] is True


def test_p26_d3_completion_receipt_safety_gate_passes_no_deploy_boundary():
    gate = evaluate_paper_release_completion_receipt_safety()
    assert gate["ok"] is True
    assert gate["status"] == "PASSED"
    assert gate["receipt_item_count"] == 12
    assert gate["deploy_enabled"] is False
    assert gate["real_money_impact"] is False
