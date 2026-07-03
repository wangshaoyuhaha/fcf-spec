import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_release_master_index import build_paper_release_master_index_operator_checklist
from btc_finance_platform.paper_release_master_index import build_paper_release_master_index_readable_report
from btc_finance_platform.paper_release_master_index import evaluate_paper_release_master_index_completion_gate


def test_p24_d4_master_index_readable_report_is_safe_and_traceable():
    report = build_paper_release_master_index_readable_report()
    assert report["ok"] is True
    assert report["title"] == "P24 Paper Release Master Index Readable Report"
    assert report["entry_count"] == 10
    assert report["deploy_enabled"] is False
    assert report["real_trading_enabled"] is False


def test_p24_d5_master_index_operator_checklist_has_required_no_deploy_checks():
    checklist = build_paper_release_master_index_operator_checklist()
    assert checklist["ok"] is True
    assert checklist["check_count"] == 12
    assert any(item["item"] == "no deploy confirmed" for item in checklist["checklist"])
    assert any(item["item"] == "no real trading confirmed" for item in checklist["checklist"])
    assert checklist["operator_review_required"] is True


def test_p24_d6_master_index_completion_gate_passes_all_required_checks():
    gate = evaluate_paper_release_master_index_completion_gate()
    assert gate["ok"] is True
    assert gate["status"] == "PASSED"
    assert gate["all_required_checks_ready"] is True
    assert gate["entry_count"] == 10
    assert gate["real_trading_enabled"] is False
