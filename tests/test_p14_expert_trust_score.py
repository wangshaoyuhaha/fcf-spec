import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_expert_trust_score import build_expert_trust_report
from btc_finance_platform.p14_expert_trust_score import score_expert_outcome
from btc_finance_platform.p14_expert_trust_score import write_expert_trust_report


def test_score_expert_outcome_rewards_recent_win():
    score = score_expert_outcome("long", "win", 0.8, age_days=0)

    assert score["weighted_score"] == 0.8
    assert score["real_world_actions_allowed"] is False


def test_score_expert_outcome_penalizes_loss():
    score = score_expert_outcome("short", "loss", 0.6, age_days=0)

    assert score["weighted_score"] == -0.6


def test_score_expert_outcome_applies_half_life_decay():
    score = score_expert_outcome("long", "win", 1.0, age_days=30, half_life_days=30)

    assert score["weighted_score"] == pytest.approx(0.5)


def test_score_expert_outcome_rejects_invalid_confidence():
    with pytest.raises(ValueError, match="confidence must be between 0 and 1"):
        score_expert_outcome("long", "win", 1.2)


def test_build_expert_trust_report_groups_by_regime_and_expert():
    report = build_expert_trust_report(
        [
            {"expert_id": "momentum", "regime": "trend_up", "direction": "long", "outcome": "win", "confidence": 0.8},
            {"expert_id": "momentum", "regime": "trend_up", "direction": "long", "outcome": "loss", "confidence": 0.4},
            {"expert_id": "smc", "regime": "range_chop", "direction": "flat", "outcome": "win", "confidence": 0.7},
        ]
    )

    assert report["row_count"] == 2
    assert report["report_status"] == "READY_FOR_OPERATOR_REVIEW"
    assert report["governor_weight_auto_apply_allowed"] is False
    assert report["real_world_actions_allowed"] is False


def test_write_expert_trust_report_creates_json(tmp_path):
    output = tmp_path / "expert_trust_report.json"

    result = write_expert_trust_report(
        [
            {"expert_id": "macro", "regime": "trend_down", "direction": "short", "outcome": "win", "confidence": 0.9}
        ],
        output,
    )

    assert result["ok"] is True
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["type"] == "p14_expert_trust_report"
    assert data["governor_weight_auto_apply_allowed"] is False
