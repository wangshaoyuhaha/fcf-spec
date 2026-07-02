import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_final_archive_closeout import evaluate_p12_final_archive_closeout
from btc_finance_platform.paper_final_archive_closeout import summarize_p12_final_archive_closeout

def report(extra=None):
    data = {
        "paper_final_release_ready": True,
        "paper_final_release_accepted": True,
        "paper_final_release_archive_ready": True,
        "paper_archive_acceptance_accepted": True,
        "paper_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
    }
    if extra:
        data.update(extra)
    return data

def days():
    return [f"P12-D{i}" for i in range(1, 16)]

def test_p12_final_archive_closeout_completes_with_all_reports():
    result = evaluate_p12_final_archive_closeout(report(), report(), report(), report(), days())
    assert result["closeout_status"] == "completed"
    assert result["p12_completed"] is True
    assert result["final_archive_completed"] is True
    assert result["real_world_actions_allowed"] is False

def test_p12_final_archive_closeout_blocks_missing_day():
    result = evaluate_p12_final_archive_closeout(report(), report(), report(), report(), days()[:-1])
    assert result["closeout_status"] == "blocked"
    assert "P12-D15" in result["missing_days"]
    assert "check_failed:all_p12_days_completed" in result["blocked_reasons"]

def test_p12_final_archive_closeout_blocks_unaccepted_release():
    result = evaluate_p12_final_archive_closeout(report(), report({"paper_final_release_accepted": False}), report(), report(), days())
    assert result["closeout_status"] == "blocked"
    assert "check_failed:release_acceptance_accepted" in result["blocked_reasons"]

def test_p12_final_archive_closeout_blocks_unaccepted_archive():
    result = evaluate_p12_final_archive_closeout(report(), report(), report(), report({"paper_archive_acceptance_accepted": False}), days())
    assert result["closeout_status"] == "blocked"
    assert "check_failed:archive_acceptance_accepted" in result["blocked_reasons"]

def test_p12_final_archive_closeout_blocks_real_action_flag():
    result = evaluate_p12_final_archive_closeout(report({"real_execution": True}), report(), report(), report(), days())
    assert result["closeout_status"] == "blocked"
    assert "check_failed:no_forbidden_real_action_flags" in result["blocked_reasons"]
    assert result["real_execution"] is False

def test_p12_final_archive_closeout_summary_keeps_safety_boundary():
    closeout = evaluate_p12_final_archive_closeout(report(), report(), report(), report(), days())
    summary = summarize_p12_final_archive_closeout(closeout)
    assert summary["status"] == "completed"
    assert summary["paper_only"] is True
    assert summary["real_execution"] is False

def test_p12_final_archive_closeout_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="release_package_summary must be a dict"):
        evaluate_p12_final_archive_closeout(None, report(), report(), report(), days())
    with pytest.raises(ValueError, match="completed_days must be a list"):
        evaluate_p12_final_archive_closeout(report(), report(), report(), report(), "bad")
