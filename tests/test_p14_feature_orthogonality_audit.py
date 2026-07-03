import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_feature_orthogonality_audit import build_feature_orthogonality_audit_report
from btc_finance_platform.p14_feature_orthogonality_audit import classify_feature_overlap
from btc_finance_platform.p14_feature_orthogonality_audit import recommend_redundant_feature_action
from btc_finance_platform.p14_feature_orthogonality_audit import write_feature_orthogonality_audit_report


def test_classify_feature_overlap_detects_high_redundancy():
    assert classify_feature_overlap(0.90) == "high_redundancy_review_required"


def test_classify_feature_overlap_detects_medium_overlap():
    assert classify_feature_overlap(0.70) == "medium_overlap_watch"


def test_classify_feature_overlap_detects_orthogonal_enough():
    assert classify_feature_overlap(0.20) == "orthogonal_enough"


def test_recommend_redundant_feature_action_prefers_review_not_auto_mute():
    row = recommend_redundant_feature_action(
        {
            "feature_a": "rsi_14",
            "feature_b": "kdj_k",
            "correlation": 0.91,
            "cost_a": 1.0,
            "cost_b": 3.0,
        }
    )

    assert row["overlap_class"] == "high_redundancy_review_required"
    assert row["proposed_review_action"] == "review_mute_or_deprioritize:kdj_k"
    assert row["auto_mute_allowed"] is False
    assert row["operator_review_required"] is True


def test_orthogonality_audit_report_counts_high_redundancy():
    report = build_feature_orthogonality_audit_report(
        [
            {"feature_a": "rsi", "feature_b": "kdj", "correlation": 0.92},
            {"feature_a": "volume", "feature_b": "macro", "correlation": 0.18},
        ]
    )

    assert report["high_redundancy_count"] == 1
    assert report["audit_status"] == "READY_FOR_OPERATOR_REVIEW"
    assert report["audit_policy"]["auto_prune_allowed"] is False


def test_orthogonality_audit_preserves_paper_only_boundary():
    report = build_feature_orthogonality_audit_report(
        [{"feature_a": "a", "feature_b": "b", "correlation": 0.10}]
    )

    assert report["paper_only"] is True
    assert report["local_only"] is True
    assert report["operator_review_required"] is True
    assert report["real_world_actions_allowed"] is False
    assert report["real_execution"] is False


def test_orthogonality_audit_rejects_missing_features():
    with pytest.raises(ValueError, match="feature_a and feature_b are required"):
        recommend_redundant_feature_action({"feature_a": "rsi", "correlation": 0.9})


def test_write_feature_orthogonality_audit_report_creates_json(tmp_path):
    output = tmp_path / "feature_orthogonality_audit_report.json"

    result = write_feature_orthogonality_audit_report(
        [{"feature_a": "rsi", "feature_b": "macd", "correlation": 0.88}],
        output,
    )

    assert result["ok"] is True
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["type"] == "p14_feature_orthogonality_audit_report"
    assert data["audit_policy"]["auto_mute_allowed"] is False
