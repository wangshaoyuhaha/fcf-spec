import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_final_release_archive_acceptance import build_paper_final_release_archive_acceptance_gate
from btc_finance_platform.paper_final_release_archive_acceptance import summarize_paper_final_release_archive_acceptance


def archive_summary(extra=None):
    data = {
        "paper_final_release_archive_ready": True,
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
        "archive_manifest_reviewed": True,
        "archive_items_verified": True,
        "validation_record_verified": True,
        "paper_only_boundary_verified": True,
        "operator_review_record_verified": True,
        "final_archive_location_recorded": True,
    }
    if extra:
        data.update(extra)
    return data


def operator_record(extra=None):
    data = {"operator_reviewed": True, "operator_accepted": True}
    if extra:
        data.update(extra)
    return data


def test_archive_acceptance_accepts_complete_paper_archive():
    result = build_paper_final_release_archive_acceptance_gate(archive_summary(), checklist(), operator_record())
    assert result["acceptance_status"] == "accepted"
    assert result["paper_archive_acceptance_accepted"] is True
    assert result["real_world_actions_allowed"] is False


def test_archive_acceptance_blocks_missing_checklist_item():
    result = build_paper_final_release_archive_acceptance_gate(
        archive_summary(),
        checklist({"final_archive_location_recorded": False}),
        operator_record(),
    )
    assert result["acceptance_status"] == "blocked"
    assert "final_archive_location_recorded" in result["missing_acceptance_items"]


def test_archive_acceptance_blocks_without_operator_acceptance():
    result = build_paper_final_release_archive_acceptance_gate(
        archive_summary(),
        checklist(),
        operator_record({"operator_accepted": False}),
    )
    assert result["acceptance_status"] == "blocked"
    assert "check_failed:operator_accepted" in result["blocked_reasons"]


def test_archive_acceptance_blocks_real_execution_flag():
    result = build_paper_final_release_archive_acceptance_gate(
        archive_summary({"real_execution": True}),
        checklist(),
        operator_record(),
    )
    assert result["acceptance_status"] == "blocked"
    assert "check_failed:no_forbidden_real_action_flags" in result["blocked_reasons"]
    assert result["real_execution"] is False


def test_archive_acceptance_summary_keeps_safety_boundary():
    gate = build_paper_final_release_archive_acceptance_gate(archive_summary(), checklist(), operator_record())
    summary = summarize_paper_final_release_archive_acceptance(gate)
    assert summary["status"] == "accepted"
    assert summary["paper_only"] is True
    assert summary["deployment_allowed_now"] is False
    assert summary["real_execution"] is False


def test_archive_acceptance_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="archive_manifest_summary must be a dict"):
        build_paper_final_release_archive_acceptance_gate(None, checklist(), operator_record())
    with pytest.raises(ValueError, match="acceptance_checklist must be a dict"):
        build_paper_final_release_archive_acceptance_gate(archive_summary(), None, operator_record())
