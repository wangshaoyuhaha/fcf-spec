import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_deployment_dry_run import build_paper_deployment_dry_run_plan
from btc_finance_platform.paper_deployment_dry_run import summarize_paper_deployment_dry_run


def preflight():
    return {
        "paper_preflight_passed": True,
        "paper_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
    }


def steps():
    return [
        "load_paper_handoff_pack",
        "verify_paper_preflight_gate",
        "simulate_config_render",
        "simulate_operator_review_checkpoint",
        "simulate_rollback_checkpoint",
    ]


def test_dry_run_ready_when_preflight_and_steps_are_complete():
    result = build_paper_deployment_dry_run_plan(preflight(), steps(), {"paper_only": True})
    assert result["dry_run_status"] == "ready"
    assert result["paper_dry_run_ready"] is True
    assert result["real_world_actions_allowed"] is False


def test_dry_run_blocks_when_step_is_missing():
    bad_steps = steps()[:-1]
    result = build_paper_deployment_dry_run_plan(preflight(), bad_steps, {"paper_only": True})
    assert result["dry_run_status"] == "blocked"
    assert "simulate_rollback_checkpoint" in result["missing_steps"]


def test_dry_run_blocks_when_preflight_failed():
    bad_preflight = preflight()
    bad_preflight["paper_preflight_passed"] = False
    result = build_paper_deployment_dry_run_plan(bad_preflight, steps(), {"paper_only": True})
    assert result["dry_run_status"] == "blocked"
    assert "check_failed:preflight_passed" in result["blocked_reasons"]


def test_dry_run_blocks_real_order_flag():
    bad_context = {"paper_only": True, "real_order": True}
    result = build_paper_deployment_dry_run_plan(preflight(), steps(), bad_context)
    assert result["dry_run_status"] == "blocked"
    assert "check_failed:no_forbidden_real_action_flags" in result["blocked_reasons"]


def test_dry_run_summary_keeps_safety_boundary():
    plan = build_paper_deployment_dry_run_plan(preflight(), steps(), {"paper_only": True})
    result = summarize_paper_deployment_dry_run(plan)
    assert result["status"] == "ready"
    assert result["paper_only"] is True
    assert result["real_world_actions_allowed"] is False
    assert result["real_execution"] is False


def test_dry_run_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="preflight_summary must be a dict"):
        build_paper_deployment_dry_run_plan(None, steps())
    with pytest.raises(ValueError, match="dry_run_steps must be a list"):
        build_paper_deployment_dry_run_plan(preflight(), "bad")
