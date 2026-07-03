import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_evidence_master_closeout import build_paper_evidence_master_closeout_packet
from btc_finance_platform.paper_evidence_master_closeout import build_paper_evidence_master_closeout_summary
from btc_finance_platform.paper_evidence_master_closeout import evaluate_paper_evidence_master_closeout_safety


def test_p21_d1_master_closeout_packet_covers_p14_to_p20():
    packet = build_paper_evidence_master_closeout_packet()
    assert packet["ok"] is True
    assert packet["release_tag"] == "v14-learning-engine-paper"
    assert len(packet["covered_phases"]) == 7
    assert packet["handoff_status"] == "READY_FOR_FINAL_ARCHIVE"
    assert packet["real_trading_enabled"] is False


def test_p21_d2_master_closeout_safety_gate_passes():
    gate = evaluate_paper_evidence_master_closeout_safety()
    assert gate["ok"] is True
    assert gate["status"] == "PASSED"
    assert gate["covered_phase_count"] == 7
    assert gate["deploy_enabled"] is False
    assert gate["real_money_impact"] is False


def test_p21_d3_master_closeout_summary_is_operator_ready():
    summary = build_paper_evidence_master_closeout_summary()
    assert summary["ok"] is True
    assert summary["title"] == "P21 Paper Evidence Console Master Closeout"
    assert summary["covered_phase_count"] == 7
    assert summary["safety_gate_status"] == "PASSED"
    assert summary["operator_review_required"] is True
