import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_master_index import build_paper_release_master_index
from btc_finance_platform.paper_release_master_index import evaluate_paper_release_master_index_safety
from btc_finance_platform.paper_release_master_index import summarize_paper_release_master_index


def test_p24_d1_master_index_lists_p14_to_p23():
    index = build_paper_release_master_index()
    assert index["ok"] is True
    assert index["release_tag"] == "v14-learning-engine-paper"
    assert index["entry_count"] == 10
    assert index["source_handoff_status"] == "READY_FOR_SNAPSHOT_ARCHIVE"
    assert index["real_trading_enabled"] is False


def test_p24_d2_master_index_summary_confirms_all_entries_indexed():
    summary = summarize_paper_release_master_index()
    assert summary["ok"] is True
    assert summary["entry_count"] == 10
    assert summary["indexed_count"] == 10
    assert summary["latest_phase"] == "P23"
    assert summary["read_only"] is True


def test_p24_d3_master_index_safety_gate_passes_no_deploy_boundary():
    gate = evaluate_paper_release_master_index_safety()
    assert gate["ok"] is True
    assert gate["status"] == "PASSED"
    assert gate["entry_count"] == 10
    assert gate["deploy_enabled"] is False
    assert gate["real_money_impact"] is False
