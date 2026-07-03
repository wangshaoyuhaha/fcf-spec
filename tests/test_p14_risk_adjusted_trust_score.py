import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_risk_adjusted_trust_score import apply_drawdown_penalty
from btc_finance_platform.p14_risk_adjusted_trust_score import build_risk_adjusted_trust_report
from btc_finance_platform.p14_risk_adjusted_trust_score import score_risk_adjusted_expert_outcome
from btc_finance_platform.p14_risk_adjusted_trust_score import write_risk_adjusted_trust_report


def test_drawdown_penalty_reduces_positive_score():
    result = apply_drawdown_penalty(1.0, 0.25, penalty_multiplier=2.0)

    assert result["penalty_factor"] == pytest.approx(1.0 / 1.5)
    assert result["risk_adjusted_score"] == pytest.approx(1.0 / 1.5)


def test_zero_drawdown_keeps_score_unchanged():
    result = apply_drawdown_penalty(0.8, 0.0)

    assert result["risk_adjusted_score"] == pytest.approx(0.8)


def test_risk_adjusted_outcome_penalizes_deep_paper_drawdown():
    smooth = score_risk_adjusted_expert_outcome("long", "win", 0.8, max_paper_drawdown_pct=0.02)
    deep = score_risk_adjusted_expert_outcome("long", "win", 0.8, max_paper_drawdown_pct=0.30)

    assert smooth["risk_adjusted_score"] > deep["risk_adjusted_score"]
    assert deep["real_world_actions_allowed"] is False


def test_risk_adjusted_trust_report_orders_smoother_path_higher():
    report = build_risk_adjusted_trust_report(
        [
            {
                "expert_id": "deep",
                "regime": "trend_up",
                "direction": "long",
                "outcome": "win",
                "confidence": 0.8,
                "max_paper_drawdown_pct": 0.30,
            },
            {
                "expert_id": "smooth",
                "regime": "trend_up",
                "direction": "long",
                "outcome": "win",
                "confidence": 0.8,
                "max_paper_drawdown_pct": 0.02,
            },
        ]
    )

    assert report["rows"][0]["expert_id"] == "smooth"
    assert report["governor_weight_auto_apply_allowed"] is False


def test_risk_adjusted_trust_report_preserves_safety_boundary():
    report = build_risk_adjusted_trust_report(
        [
            {
                "expert_id": "macro",
                "regime": "liquidity_stress",
                "direction": "observe",
                "outcome": "neutral",
                "confidence": 0.5,
            }
        ]
    )

    assert report["paper_only"] is True
    assert report["local_only"] is True
    assert report["operator_review_required"] is True
    assert report["real_world_actions_allowed"] is False
    assert report["real_execution"] is False


def test_drawdown_penalty_rejects_invalid_drawdown():
    with pytest.raises(ValueError, match="max_paper_drawdown_pct must be between 0 and 1"):
        apply_drawdown_penalty(1.0, 1.5)


def test_write_risk_adjusted_trust_report_creates_json(tmp_path):
    output = tmp_path / "risk_adjusted_trust_report.json"

    result = write_risk_adjusted_trust_report(
        [
            {
                "expert_id": "momentum",
                "regime": "trend_up",
                "direction": "long",
                "outcome": "win",
                "confidence": 0.8,
                "max_paper_drawdown_pct": 0.05,
            }
        ],
        output,
    )

    assert result["ok"] is True
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["type"] == "p14_risk_adjusted_trust_report"
    assert data["governor_weight_auto_apply_allowed"] is False
