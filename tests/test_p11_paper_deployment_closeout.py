import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_deployment_closeout import evaluate_p11_paper_deployment_closeout
from btc_finance_platform.paper_deployment_closeout import summarize_p11_paper_deployment_closeout


def report(extra=None):
    data = {
        "paper_deployment_handoff_ready": True,
        "paper_preflight_passed": True,
        "paper_dry_run_ready": True,
        "paper_dry_run_report_accepted": True,
        "paper_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
    }
    if extra:
        data.update(extra)
    return data


def days():
    return [f"P11-D{i}" for i in range(1, 16)]


def test_p11_closeout_completes_with_all_paper_reports():
    result = evaluate_p11_paper_deployment_closeout(report(), report(), report(), report(), days())
    assert result["closeout_status"] == "completed"
    assert result["p11_completed"] is True
    assert result["next_stage"] == "P12"
    assert result["real_world_actions_allowed"] is False


def test_p11_closeout_blocks_missing_day():
    result = evaluate_p11_paper_deployment_closeout(report(), report(), report(), report(), days()[:-1])
    assert result["closeout_status"] == "blocked"
    assert "P11-D15" in result["missing_days"]
    assert "check_failed:all_p11_days_completed" in result["blocked_reasons"]


def test_p11_closeout_blocks_failed_preflight():
    bad_preflight = report({"paper_preflight_passed": False})
    result = evaluate_p11_paper_deployment_closeout(report(), bad_preflight, report(), report(), days())
    assert result["closeout_status"] == "blocked"
    assert "check_failed:preflight_passed" in result["blocked_reasons"]


def test_p11_closeout_blocks_unaccepted_dry_run_report():
    bad_report = report({"paper_dry_run_report_accepted": False})
    result = evaluate_p11_paper_deployment_closeout(report(), report(), report(), bad_report, days())
    assert result["closeout_status"] == "blocked"
    assert "check_failed:dry_run_report_accepted" in result["blocked_reasons"]


def test_p11_closeout_blocks_real_world_flag():
    bad_dry_run = report({"real_world_actions_allowed": False})
    result = evaluate_p11_paper_deployment_closeout(report(), report(), bad_dry_run, report(), days())
    assert result["closeout_status"] == "blocked"
    assert "check_failed:no_forbidden_real_action_flags" in result["blocked_reasons"]
    assert result["deployment_allowed_now"] is False


def test_p11_closeout_summary_keeps_safety_boundary():
    closeout = evaluate_p11_paper_deployment_closeout(report(), report(), report(), report(), days())
    summary = summarize_p11_paper_deployment_closeout(closeout)
    assert summary["status"] == "completed"
    assert summary["p11_completed"] is True
    assert summary["paper_only"] is True
    assert summary["real_execution"] is False


def test_p11_closeout_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="handoff_summary must be a dict"):
        evaluate_p11_paper_deployment_closeout(None, report(), report(), report(), days())
    with pytest.raises(ValueError, match="completed_days must be a list"):
        evaluate_p11_paper_deployment_closeout(report(), report(), report(), report(), "bad")
