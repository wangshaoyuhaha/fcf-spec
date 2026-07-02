import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_deployment_preflight import build_paper_deployment_preflight_gate
from btc_finance_platform.paper_deployment_preflight import summarize_paper_deployment_preflight


def handoff():
    return {
        "paper_deployment_handoff_ready": True,
        "paper_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "parameter_update_allowed_now": False,
    }


def checklist():
    return {
        "paper_handoff_pack_reviewed": True,
        "model_card_reviewed": True,
        "readiness_gate_reviewed": True,
        "risk_policy_boundary_reviewed": True,
        "rollback_plan_reviewed": True,
    }


def test_preflight_passes_with_complete_paper_checklist():
    result = build_paper_deployment_preflight_gate(handoff(), checklist(), {"paper_only": True})
    assert result["preflight_status"] == "passed"
    assert result["paper_preflight_passed"] is True
    assert result["real_world_actions_allowed"] is False


def test_preflight_blocks_missing_checklist_item():
    bad = checklist()
    bad["rollback_plan_reviewed"] = False
    result = build_paper_deployment_preflight_gate(handoff(), bad, {"paper_only": True})
    assert result["preflight_status"] == "blocked"
    assert "rollback_plan_reviewed" in result["missing_checklist_items"]


def test_preflight_blocks_real_execution_flag():
    bad_handoff = handoff()
    bad_handoff["real_execution"] = True
    result = build_paper_deployment_preflight_gate(bad_handoff, checklist(), {"paper_only": True})
    assert result["preflight_status"] == "blocked"
    assert "check_failed:no_forbidden_real_action_flags" in result["blocked_reasons"]


def test_preflight_blocks_non_paper_runtime_context():
    result = build_paper_deployment_preflight_gate(handoff(), checklist(), {"paper_only": False})
    assert result["preflight_status"] == "blocked"
    assert "check_failed:runtime_context_paper_only" in result["blocked_reasons"]


def test_preflight_summary_keeps_safety_boundary():
    preflight = build_paper_deployment_preflight_gate(handoff(), checklist(), {"paper_only": True})
    summary = summarize_paper_deployment_preflight(preflight)
    assert summary["status"] == "passed"
    assert summary["paper_only"] is True
    assert summary["deployment_allowed_now"] is False
    assert summary["operator_review_required"] is True


def test_preflight_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="handoff_pack must be a dict"):
        build_paper_deployment_preflight_gate(None, checklist())
    with pytest.raises(ValueError, match="operator_checklist must be a dict"):
        build_paper_deployment_preflight_gate(handoff(), None)
