import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_final_release_package import build_paper_final_release_package
from btc_finance_platform.paper_final_release_package import summarize_paper_final_release_package


def p10(extra=None):
    data = {"p10_completed": True, "paper_only": True, "operator_review_required": True}
    if extra:
        data.update(extra)
    return data


def p11(extra=None):
    data = {"p11_completed": True, "paper_only": True, "operator_review_required": True}
    if extra:
        data.update(extra)
    return data


def validation(extra=None):
    data = {"all_checks_passed": True, "pytest_passed": True, "paper_only": True, "operator_review_required": True}
    if extra:
        data.update(extra)
    return data


def sections():
    return [
        "project_state_summary",
        "p10_model_registry_closeout",
        "p11_paper_deployment_closeout",
        "validation_summary",
        "paper_only_safety_boundary",
        "operator_review_record",
    ]


def test_final_release_package_ready_with_completed_p10_p11_and_validation():
    result = build_paper_final_release_package(p10(), p11(), validation(), sections())
    assert result["release_status"] == "ready"
    assert result["paper_final_release_ready"] is True
    assert result["real_world_actions_allowed"] is False


def test_final_release_package_blocks_missing_section():
    result = build_paper_final_release_package(p10(), p11(), validation(), sections()[:-1])
    assert result["release_status"] == "blocked"
    assert "operator_review_record" in result["missing_sections"]


def test_final_release_package_blocks_failed_validation():
    result = build_paper_final_release_package(p10(), p11(), validation({"pytest_passed": False}), sections())
    assert result["release_status"] == "blocked"
    assert "check_failed:validation_passed" in result["blocked_reasons"]


def test_final_release_package_blocks_real_action_flag():
    result = build_paper_final_release_package(p10({"real_order": True}), p11(), validation(), sections())
    assert result["release_status"] == "blocked"
    assert "check_failed:no_forbidden_real_action_flags" in result["blocked_reasons"]
    assert result["real_order"] is False


def test_final_release_summary_keeps_safety_boundary():
    package = build_paper_final_release_package(p10(), p11(), validation(), sections())
    summary = summarize_paper_final_release_package(package)
    assert summary["status"] == "ready"
    assert summary["paper_only"] is True
    assert summary["deployment_allowed_now"] is False
    assert summary["real_execution"] is False


def test_final_release_package_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="p10_closeout must be a dict"):
        build_paper_final_release_package(None, p11(), validation(), sections())
    with pytest.raises(ValueError, match="sections must be a list"):
        build_paper_final_release_package(p10(), p11(), validation(), "bad")
