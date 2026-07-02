import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_final_release_acceptance import build_paper_final_release_acceptance_gate
from btc_finance_platform.paper_final_release_acceptance import summarize_paper_final_release_acceptance


def release_summary(extra=None):
    data = {
        "paper_final_release_ready": True,
        "paper_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
    }
    if extra:
        data.update(extra)
    return data


def checklist(extra=None):
    data = {
        "release_package_reviewed": True,
        "validation_summary_reviewed": True,
        "paper_only_boundary_reviewed": True,
        "operator_review_recorded": True,
        "rollback_notes_reviewed": True,
        "next_stage_handoff_reviewed": True,
    }
    if extra:
        data.update(extra)
    return data


def operator_record(extra=None):
    data = {"operator_reviewed": True, "operator_accepted": True}
    if extra:
        data.update(extra)
    return data


def test_acceptance_gate_accepts_complete_paper_release():
    result = build_paper_final_release_acceptance_gate(release_summary(), checklist(), operator_record())
    assert result["acceptance_status"] == "accepted"
    assert result["paper_final_release_accepted"] is True
    assert result["real_world_actions_allowed"] is False


def test_acceptance_gate_blocks_missing_checklist_item():
    result = build_paper_final_release_acceptance_gate(
        release_summary(),
        checklist({"rollback_notes_reviewed": False}),
        operator_record(),
    )
    assert result["acceptance_status"] == "blocked"
    assert "rollback_notes_reviewed" in result["missing_acceptance_items"]


def test_acceptance_gate_blocks_without_operator_acceptance():
    result = build_paper_final_release_acceptance_gate(
        release_summary(),
        checklist(),
        operator_record({"operator_accepted": False}),
    )
    assert result["acceptance_status"] == "blocked"
    assert "check_failed:operator_accepted" in result["blocked_reasons"]


def test_acceptance_gate_blocks_real_deployment_flag():
    result = build_paper_final_release_acceptance_gate(
        release_summary({"deployment_allowed_now": True}),
        checklist(),
        operator_record(),
    )
    assert result["acceptance_status"] == "blocked"
    assert "check_failed:no_forbidden_real_action_flags" in result["blocked_reasons"]
    assert result["deployment_allowed_now"] is False


def test_acceptance_summary_keeps_safety_boundary():
    gate = build_paper_final_release_acceptance_gate(release_summary(), checklist(), operator_record())
    summary = summarize_paper_final_release_acceptance(gate)
    assert summary["status"] == "accepted"
    assert summary["paper_only"] is True
    assert summary["real_execution"] is False


def test_acceptance_gate_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="release_package_summary must be a dict"):
        build_paper_final_release_acceptance_gate(None, checklist(), operator_record())
    with pytest.raises(ValueError, match="acceptance_checklist must be a dict"):
        build_paper_final_release_acceptance_gate(release_summary(), None, operator_record())
