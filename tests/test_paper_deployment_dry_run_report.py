import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_deployment_dry_run_report import build_paper_deployment_dry_run_report
from btc_finance_platform.paper_deployment_dry_run_report import summarize_paper_deployment_dry_run_report


def plan():
    return {
        "paper_dry_run_ready": True,
        "paper_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
    }


def observations():
    return {
        "handoff_pack_loaded": True,
        "preflight_gate_verified": True,
        "config_render_simulated": True,
        "operator_checkpoint_simulated": True,
        "rollback_checkpoint_simulated": True,
    }


def review():
    return {
        "operator_reviewed": True,
        "operator_approved": True,
    }


def test_dry_run_report_accepted_when_plan_observations_and_review_are_complete():
    result = build_paper_deployment_dry_run_report(plan(), observations(), review())
    assert result["report_status"] == "accepted"
    assert result["paper_dry_run_report_accepted"] is True
    assert result["real_world_actions_allowed"] is False


def test_dry_run_report_blocks_missing_observation():
    bad = observations()
    bad["rollback_checkpoint_simulated"] = False
    result = build_paper_deployment_dry_run_report(plan(), bad, review())
    assert result["report_status"] == "blocked"
    assert "rollback_checkpoint_simulated" in result["missing_observations"]


def test_dry_run_report_blocks_without_operator_approval():
    bad_review = review()
    bad_review["operator_approved"] = False
    result = build_paper_deployment_dry_run_report(plan(), observations(), bad_review)
    assert result["report_status"] == "blocked"
    assert "check_failed:operator_approved" in result["blocked_reasons"]


def test_dry_run_report_blocks_real_execution_flag():
    bad_plan = plan()
    bad_plan["real_execution"] = True
    result = build_paper_deployment_dry_run_report(bad_plan, observations(), review())
    assert result["report_status"] == "blocked"
    assert "check_failed:no_forbidden_real_action_flags" in result["blocked_reasons"]


def test_dry_run_report_summary_keeps_safety_boundary():
    report = build_paper_deployment_dry_run_report(plan(), observations(), review())
    result = summarize_paper_deployment_dry_run_report(report)
    assert result["status"] == "accepted"
    assert result["paper_only"] is True
    assert result["deployment_allowed_now"] is False
    assert result["real_execution"] is False


def test_dry_run_report_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="dry_run_plan must be a dict"):
        build_paper_deployment_dry_run_report(None, observations(), review())
    with pytest.raises(ValueError, match="observations must be a dict"):
        build_paper_deployment_dry_run_report(plan(), None, review())
