import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_evidence_snapshot import build_paper_release_evidence_snapshot
from btc_finance_platform.paper_release_evidence_snapshot import evaluate_paper_release_evidence_snapshot_safety
from btc_finance_platform.paper_release_evidence_snapshot import summarize_paper_release_evidence_snapshot


def test_p23_d1_snapshot_covers_p14_to_p22():
    snapshot = build_paper_release_evidence_snapshot()
    assert snapshot["ok"] is True
    assert snapshot["release_tag"] == "v14-learning-engine-paper"
    assert snapshot["item_count"] == 9
    assert snapshot["deploy_enabled"] is False
    assert snapshot["real_trading_enabled"] is False


def test_p23_d2_snapshot_summary_confirms_all_items_complete_or_released():
    summary = summarize_paper_release_evidence_snapshot()
    assert summary["ok"] is True
    assert summary["item_count"] == 9
    assert summary["completed_or_released_count"] == 9
    assert summary["latest_phase"] == "P22"
    assert summary["read_only"] is True


def test_p23_d3_snapshot_safety_gate_passes_no_deploy_boundary():
    gate = evaluate_paper_release_evidence_snapshot_safety()
    assert gate["ok"] is True
    assert gate["status"] == "PASSED"
    assert gate["item_count"] == 9
    assert gate["deploy_enabled"] is False
    assert gate["real_money_impact"] is False
