import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_meta_anomaly_detection import build_meta_anomaly_report
from btc_finance_platform.p14_meta_anomaly_detection import classify_confidence_anomaly
from btc_finance_platform.p14_meta_anomaly_detection import classify_drawdown_anomaly
from btc_finance_platform.p14_meta_anomaly_detection import evaluate_meta_anomaly_window
from btc_finance_platform.p14_meta_anomaly_detection import write_meta_anomaly_report


def test_classify_confidence_anomaly_detects_overconfidence():
    assert classify_confidence_anomaly(0.91, 0.35) == "overconfidence_anomaly"


def test_classify_confidence_anomaly_detects_normal_case():
    assert classify_confidence_anomaly(0.70, 0.58) == "normal"


def test_classify_drawdown_anomaly_detects_critical_drawdown():
    assert classify_drawdown_anomaly(0.35) == "critical_paper_drawdown"


def test_evaluate_meta_anomaly_window_proposes_shadow_review():
    result = evaluate_meta_anomaly_window(
        {
            "window_id": "test_window",
            "average_confidence": 0.91,
            "actual_win_rate": 0.35,
            "max_paper_drawdown_pct": 0.10,
        }
    )

    assert "overconfidence_anomaly" in result["anomaly_flags"]
    assert result["proposed_mode"] == "force_shadow_review"
    assert result["auto_mode_switch_allowed"] is False


def test_meta_anomaly_report_preserves_paper_only_boundary():
    report = build_meta_anomaly_report(
        [
            {
                "window_id": "normal_window",
                "average_confidence": 0.60,
                "actual_win_rate": 0.55,
                "max_paper_drawdown_pct": 0.05,
            }
        ]
    )

    assert report["paper_only"] is True
    assert report["local_only"] is True
    assert report["operator_review_required"] is True
    assert report["real_world_actions_allowed"] is False
    assert report["real_execution"] is False


def test_meta_anomaly_rejects_invalid_confidence():
    with pytest.raises(ValueError, match="average_confidence must be between 0 and 1"):
        classify_confidence_anomaly(1.2, 0.5)


def test_write_meta_anomaly_report_creates_json(tmp_path):
    output = tmp_path / "meta_anomaly_report.json"

    result = write_meta_anomaly_report(
        [
            {
                "window_id": "last_30_days",
                "average_confidence": 0.91,
                "actual_win_rate": 0.35,
                "max_paper_drawdown_pct": 0.12,
            }
        ],
        output,
    )

    assert result["ok"] is True
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["type"] == "p14_meta_anomaly_report"
    assert data["meta_policy"]["auto_mode_switch_allowed"] is False
