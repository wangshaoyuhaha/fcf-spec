import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_final_release_archive import build_paper_final_release_archive_manifest
from btc_finance_platform.paper_final_release_archive import summarize_paper_final_release_archive_manifest


def acceptance_summary(extra=None):
    data = {
        "paper_final_release_accepted": True,
        "paper_only": True,
        "operator_review_required": True,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
    }
    if extra:
        data.update(extra)
    return data


def archive_items():
    return [
        "project_state",
        "release_package_summary",
        "acceptance_summary",
        "validation_log",
        "safety_boundary_record",
        "operator_review_record",
    ]


def validation_record(extra=None):
    data = {
        "all_checks_passed": True,
        "pytest_passed": True,
        "paper_only": True,
        "operator_review_required": True,
    }
    if extra:
        data.update(extra)
    return data


def test_archive_manifest_ready_when_acceptance_and_validation_passed():
    result = build_paper_final_release_archive_manifest(acceptance_summary(), archive_items(), validation_record())
    assert result["archive_status"] == "ready"
    assert result["paper_final_release_archive_ready"] is True
    assert result["real_world_actions_allowed"] is False


def test_archive_manifest_blocks_missing_archive_item():
    result = build_paper_final_release_archive_manifest(acceptance_summary(), archive_items()[:-1], validation_record())
    assert result["archive_status"] == "blocked"
    assert "operator_review_record" in result["missing_archive_items"]


def test_archive_manifest_blocks_failed_validation():
    result = build_paper_final_release_archive_manifest(
        acceptance_summary(),
        archive_items(),
        validation_record({"pytest_passed": False}),
    )
    assert result["archive_status"] == "blocked"
    assert "check_failed:validation_passed" in result["blocked_reasons"]


def test_archive_manifest_blocks_real_execution_flag():
    result = build_paper_final_release_archive_manifest(
        acceptance_summary({"real_execution": True}),
        archive_items(),
        validation_record(),
    )
    assert result["archive_status"] == "blocked"
    assert "check_failed:no_forbidden_real_action_flags" in result["blocked_reasons"]
    assert result["real_execution"] is False


def test_archive_summary_keeps_safety_boundary():
    manifest = build_paper_final_release_archive_manifest(acceptance_summary(), archive_items(), validation_record())
    summary = summarize_paper_final_release_archive_manifest(manifest)
    assert summary["status"] == "ready"
    assert summary["paper_only"] is True
    assert summary["deployment_allowed_now"] is False
    assert summary["real_execution"] is False


def test_archive_manifest_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="acceptance_summary must be a dict"):
        build_paper_final_release_archive_manifest(None, archive_items(), validation_record())
    with pytest.raises(ValueError, match="archive_items must be a list"):
        build_paper_final_release_archive_manifest(acceptance_summary(), "bad", validation_record())
