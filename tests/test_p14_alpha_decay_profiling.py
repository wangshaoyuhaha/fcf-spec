import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_alpha_decay_profiling import build_alpha_decay_report
from btc_finance_platform.p14_alpha_decay_profiling import classify_alpha_window
from btc_finance_platform.p14_alpha_decay_profiling import estimate_alpha_decay_profile
from btc_finance_platform.p14_alpha_decay_profiling import write_alpha_decay_report


def test_classify_alpha_window():
    assert classify_alpha_window(1) == "ultra_short_term"
    assert classify_alpha_window(12) == "short_term"
    assert classify_alpha_window(72) == "medium_term"
    assert classify_alpha_window(300) == "long_term"


def test_estimate_alpha_decay_profile_selects_best_window():
    profile = estimate_alpha_decay_profile(
        "twitter_sentiment_index",
        "sentiment",
        {"1h": 0.18, "4h": 0.31, "24h": 0.08},
    )

    assert profile["best_window_hours"] == 4
    assert profile["alpha_window_class"] == "ultra_short_term"
    assert profile["auto_weight_update_allowed"] is False
    assert profile["operator_review_required"] is True


def test_estimate_alpha_decay_profile_handles_no_positive_alpha():
    profile = estimate_alpha_decay_profile(
        "weak_source",
        "sentiment",
        {"1h": -0.1, "4h": -0.05},
    )

    assert profile["decay_status"] == "no_positive_alpha_observed"
    assert profile["suggested_usage"] == "review_or_deprioritize"


def test_alpha_decay_report_preserves_safety_boundary():
    report = build_alpha_decay_report(
        [
            {
                "source_id": "macro_uncertainty_note",
                "source_type": "macro_text",
                "window_scores": {"24h": 0.12, "72h": 0.28},
            }
        ]
    )

    assert report["paper_only"] is True
    assert report["local_only"] is True
    assert report["operator_review_required"] is True
    assert report["real_world_actions_allowed"] is False
    assert report["real_execution"] is False


def test_alpha_decay_profile_rejects_missing_source_id():
    with pytest.raises(ValueError, match="source_id is required"):
        estimate_alpha_decay_profile("", "sentiment", {"1h": 0.1})


def test_alpha_decay_profile_rejects_invalid_window_scores():
    with pytest.raises(ValueError, match="window_scores must be a non-empty dict"):
        estimate_alpha_decay_profile("source", "sentiment", {})


def test_write_alpha_decay_report_creates_json(tmp_path):
    output = tmp_path / "alpha_decay_report.json"

    result = write_alpha_decay_report(
        [
            {
                "source_id": "volume_breakout_score",
                "source_type": "market_feature",
                "window_scores": {"4h": 0.16, "24h": 0.33},
            }
        ],
        output,
    )

    assert result["ok"] is True
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["type"] == "p14_alpha_decay_report"
    assert data["audit_policy"]["auto_weight_update_allowed"] is False
