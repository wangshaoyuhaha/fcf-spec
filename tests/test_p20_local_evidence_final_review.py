import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.operator_evidence_final_review import build_local_evidence_final_review_packet
from btc_finance_platform.operator_evidence_final_review import build_local_evidence_final_review_summary
from btc_finance_platform.operator_evidence_final_review import evaluate_local_evidence_final_review_safety


def test_p20_d1_final_review_packet_covers_p14_to_p19():
    packet = build_local_evidence_final_review_packet()
    assert packet["ok"] is True
    assert packet["release_tag"] == "v14-learning-engine-paper"
    assert len(packet["review_scope"]) == 6
    assert packet["deploy_enabled"] is False
    assert packet["real_trading_enabled"] is False


def test_p20_d2_final_review_safety_gate_passes_paper_only_boundary():
    gate = evaluate_local_evidence_final_review_safety()
    assert gate["ok"] is True
    assert gate["status"] == "PASSED"
    assert gate["paper_only"] is True
    assert gate["real_money_impact"] is False
    assert gate["operator_review_required"] is True


def test_p20_d3_final_review_summary_is_ready_for_operator_inspection():
    summary = build_local_evidence_final_review_summary()
    assert summary["ok"] is True
    assert summary["title"] == "P20 Local Evidence Console Final Review"
    assert summary["review_item_count"] == 6
    assert summary["safety_gate_status"] == "PASSED"
    assert summary["read_only"] is True
