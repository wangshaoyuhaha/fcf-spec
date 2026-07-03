import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_data_quality_sentry import build_data_quality_sentry_report
from btc_finance_platform.p14_data_quality_sentry import classify_data_quality_issue
from btc_finance_platform.p14_data_quality_sentry import evaluate_data_source_quality
from btc_finance_platform.p14_data_quality_sentry import write_data_quality_sentry_report


def test_classify_data_quality_issue_clean():
    assert classify_data_quality_issue(0.0, 30, 0.0) == "clean"


def test_classify_data_quality_issue_missing_warning():
    assert classify_data_quality_issue(0.10, 30, 0.0) == "missing_data_warning"


def test_classify_data_quality_issue_stale_warning():
    assert classify_data_quality_issue(0.0, 600, 0.0) == "stale_data_warning"


def test_classify_data_quality_issue_outlier_warning():
    assert classify_data_quality_issue(0.0, 30, 0.10) == "outlier_warning"


def test_evaluate_data_source_quality_requires_operator_review():
    result = evaluate_data_source_quality(
        {
            "source_id": "paper_sentiment_feed",
            "source_type": "sentiment",
            "missing_ratio": 0.08,
            "latency_seconds": 20,
            "outlier_ratio": 0.01,
        }
    )

    assert result["quality_status"] == "missing_data_warning"
    assert result["proposed_usage"] == "quarantine_for_operator_review"
    assert result["auto_quarantine_allowed"] is False
    assert result["operator_review_required"] is True


def test_data_quality_sentry_preserves_paper_only_boundary():
    report = build_data_quality_sentry_report(
        [
            {
                "source_id": "paper_price_feed",
                "missing_ratio": 0.0,
                "latency_seconds": 30,
                "outlier_ratio": 0.0,
            }
        ]
    )

    assert report["paper_only"] is True
    assert report["local_only"] is True
    assert report["operator_review_required"] is True
    assert report["real_world_actions_allowed"] is False
    assert report["real_execution"] is False


def test_data_quality_sentry_rejects_invalid_missing_ratio():
    with pytest.raises(ValueError, match="missing_ratio must be between 0 and 1"):
        classify_data_quality_issue(1.5, 30, 0.0)


def test_write_data_quality_sentry_report_creates_json(tmp_path):
    output = tmp_path / "data_quality_sentry_report.json"

    result = write_data_quality_sentry_report(
        [
            {
                "source_id": "paper_price_feed",
                "missing_ratio": 0.0,
                "latency_seconds": 30,
                "outlier_ratio": 0.0,
            }
        ],
        output,
    )

    assert result["ok"] is True
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["type"] == "p14_data_quality_sentry_report"
    assert data["quality_policy"]["auto_quarantine_allowed"] is False
