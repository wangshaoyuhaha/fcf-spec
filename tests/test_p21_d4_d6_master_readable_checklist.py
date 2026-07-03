import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_evidence_master_closeout import build_paper_evidence_master_operator_checklist
from btc_finance_platform.paper_evidence_master_closeout import build_paper_evidence_master_readable_report
from btc_finance_platform.paper_evidence_master_closeout import evaluate_paper_evidence_master_completion_gate


def test_p21_d4_master_readable_report_covers_p14_to_p20():
    report = build_paper_evidence_master_readable_report()
    assert report["ok"] is True
    assert report["title"] == "P21 Paper Evidence Master Readable Report"
    assert report["covered_phase_count"] == 7
    assert report["deploy_enabled"] is False
    assert report["real_trading_enabled"] is False


def test_p21_d5_master_operator_checklist_has_no_deploy_and_no_real_trading_checks():
    checklist = build_paper_evidence_master_operator_checklist()
    assert checklist["ok"] is True
    assert checklist["check_count"] == 9
    assert any(item["item"] == "no deploy confirmed" for item in checklist["checklist"])
    assert any(item["item"] == "no real trading confirmed" for item in checklist["checklist"])
    assert checklist["operator_review_required"] is True


def test_p21_d6_master_completion_gate_passes_all_required_checks():
    gate = evaluate_paper_evidence_master_completion_gate()
    assert gate["ok"] is True
    assert gate["status"] == "PASSED"
    assert gate["all_required_checks_ready"] is True
    assert gate["covered_phase_count"] == 7
    assert gate["real_trading_enabled"] is False
