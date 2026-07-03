import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_evidence_snapshot import build_paper_release_evidence_snapshot_operator_checklist
from btc_finance_platform.paper_release_evidence_snapshot import build_paper_release_evidence_snapshot_readable_report
from btc_finance_platform.paper_release_evidence_snapshot import evaluate_paper_release_evidence_snapshot_completion_gate


def test_p23_d4_snapshot_readable_report_is_safe_and_traceable():
    report = build_paper_release_evidence_snapshot_readable_report()
    assert report["ok"] is True
    assert report["title"] == "P23 Paper Release Evidence Snapshot Readable Report"
    assert report["item_count"] == 9
    assert report["deploy_enabled"] is False
    assert report["real_trading_enabled"] is False


def test_p23_d5_snapshot_operator_checklist_has_no_deploy_checks():
    checklist = build_paper_release_evidence_snapshot_operator_checklist()
    assert checklist["ok"] is True
    assert checklist["check_count"] == 11
    assert any(item["item"] == "no deploy confirmed" for item in checklist["checklist"])
    assert any(item["item"] == "no real trading confirmed" for item in checklist["checklist"])
    assert checklist["operator_review_required"] is True


def test_p23_d6_snapshot_completion_gate_passes_all_required_checks():
    gate = evaluate_paper_release_evidence_snapshot_completion_gate()
    assert gate["ok"] is True
    assert gate["status"] == "PASSED"
    assert gate["all_required_checks_ready"] is True
    assert gate["item_count"] == 9
    assert gate["real_trading_enabled"] is False
