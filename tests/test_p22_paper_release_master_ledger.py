import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_master_ledger import build_paper_release_master_ledger
from btc_finance_platform.paper_release_master_ledger import evaluate_paper_release_master_ledger_safety
from btc_finance_platform.paper_release_master_ledger import summarize_paper_release_master_ledger


def test_p22_d1_master_ledger_lists_p14_to_p21():
    ledger = build_paper_release_master_ledger()
    assert ledger["ok"] is True
    assert ledger["release_tag"] == "v14-learning-engine-paper"
    assert ledger["entry_count"] == 8
    assert ledger["deploy_enabled"] is False
    assert ledger["real_trading_enabled"] is False


def test_p22_d2_master_ledger_summary_confirms_all_entries_complete_or_released():
    summary = summarize_paper_release_master_ledger()
    assert summary["ok"] is True
    assert summary["entry_count"] == 8
    assert summary["completed_or_released_count"] == 8
    assert summary["latest_phase"] == "P21"
    assert summary["read_only"] is True


def test_p22_d3_master_ledger_safety_gate_passes_no_deploy_boundary():
    gate = evaluate_paper_release_master_ledger_safety()
    assert gate["ok"] is True
    assert gate["status"] == "PASSED"
    assert gate["entry_count"] == 8
    assert gate["deploy_enabled"] is False
    assert gate["real_money_impact"] is False
