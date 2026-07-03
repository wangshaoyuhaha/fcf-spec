import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_feature_source_audit import build_feature_source_audit_report
from btc_finance_platform.p14_feature_source_audit import classify_feature_action
from btc_finance_platform.p14_feature_source_audit import write_feature_source_audit_report


def test_classify_feature_action_deprioritizes_weak_signal():
    assert classify_feature_action(0.04, 100) == "deprioritize_or_silence"


def test_classify_feature_action_keeps_strong_signal():
    assert classify_feature_action(0.35, 100) == "keep_high_priority"


def test_classify_feature_action_handles_insufficient_data():
    assert classify_feature_action(0.40, 5) == "insufficient_data"


def test_feature_source_audit_report_marks_operator_review_only():
    report = build_feature_source_audit_report(
        [
            {
                "feature_id": "twitter_sentiment_index",
                "source_type": "sentiment",
                "regime": "range_chop",
                "correlation": 0.04,
                "observation_count": 120,
            }
        ]
    )

    assert report["audit_status"] == "READY_FOR_OPERATOR_REVIEW"
    assert report["audit_policy"]["auto_prune_allowed"] is False
    assert report["operator_review_required"] is True


def test_feature_source_audit_preserves_paper_only_boundary():
    report = build_feature_source_audit_report(
        [
            {
                "feature_id": "volume_breakout_score",
                "source_type": "market_feature",
                "regime": "trend_up",
                "correlation": 0.36,
                "observation_count": 90,
            }
        ]
    )

    assert report["paper_only"] is True
    assert report["local_only"] is True
    assert report["real_world_actions_allowed"] is False
    assert report["real_order"] is False
    assert report["real_execution"] is False


def test_feature_source_audit_rejects_missing_feature_id():
    with pytest.raises(ValueError, match="feature_id is required"):
        build_feature_source_audit_report(
            [
                {
                    "source_type": "sentiment",
                    "correlation": 0.1,
                    "observation_count": 30,
                }
            ]
        )


def test_write_feature_source_audit_report_creates_json(tmp_path):
    output = tmp_path / "feature_source_audit_report.json"

    result = write_feature_source_audit_report(
        [
            {
                "feature_id": "funding_rate_bias",
                "source_type": "market_feature",
                "regime": "trend_down",
                "correlation": -0.31,
                "observation_count": 60,
            }
        ],
        output,
    )

    assert result["ok"] is True
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["type"] == "p14_feature_source_audit_report"
    assert data["audit_policy"]["auto_prune_allowed"] is False
