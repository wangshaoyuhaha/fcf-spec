import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_explanation_consistency_check import build_explanation_consistency_report
from btc_finance_platform.p14_explanation_consistency_check import check_field_consistency
from btc_finance_platform.p14_explanation_consistency_check import detect_unsafe_explanation_phrases
from btc_finance_platform.p14_explanation_consistency_check import write_explanation_consistency_report


def test_detect_unsafe_explanation_phrases():
    phrases = detect_unsafe_explanation_phrases("This says real execution allowed by mistake.")

    assert "real execution allowed" in phrases


def test_field_consistency_detects_mismatch():
    mismatches = check_field_consistency(
        {"operator_review_required": True},
        {"operator_review_required": False},
    )

    assert len(mismatches) == 1
    assert mismatches[0]["field"] == "operator_review_required"


def test_explanation_consistency_blocks_unsafe_phrase():
    report = build_explanation_consistency_report(
        {"type": "sample", "real_execution": False},
        "real execution allowed",
        {"real_execution": False},
    )

    assert report["blocked"] is True
    assert report["consistency_status"] == "BLOCKED_FOR_OPERATOR_REVIEW"


def test_explanation_consistency_blocks_claim_mismatch():
    report = build_explanation_consistency_report(
        {"type": "sample", "real_order": False},
        "paper-only explanation",
        {"real_order": True},
    )

    assert report["blocked"] is True
    assert report["mismatch_count"] == 1


def test_explanation_consistency_passes_safe_explanation():
    report = build_explanation_consistency_report(
        {
            "type": "sample",
            "paper_only": True,
            "operator_review_required": True,
            "real_world_actions_allowed": False,
        },
        "paper-only report, operator review required",
        {
            "paper_only": True,
            "operator_review_required": True,
            "real_world_actions_allowed": False,
        },
    )

    assert report["blocked"] is False
    assert report["consistency_status"] == "CONSISTENT_READY_FOR_OPERATOR_REVIEW"


def test_explanation_consistency_preserves_safety_boundary():
    report = build_explanation_consistency_report(
        {"type": "sample"},
        "paper-only local explanation",
        {},
    )

    assert report["paper_only"] is True
    assert report["local_only"] is True
    assert report["operator_review_required"] is True
    assert report["real_world_actions_allowed"] is False
    assert report["real_execution"] is False


def test_write_explanation_consistency_report_creates_json(tmp_path):
    output = tmp_path / "explanation_consistency_report.json"

    result = write_explanation_consistency_report(
        {"type": "sample", "paper_only": True},
        "paper-only explanation",
        {"paper_only": True},
        output,
    )

    assert result["ok"] is True
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["type"] == "p14_explanation_consistency_report"
    assert data["consistency_policy"]["ai_explanation_override_allowed"] is False
