import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_governor_weight_proposal import apply_meta_anomaly_guard
from btc_finance_platform.p14_governor_weight_proposal import build_governor_weight_proposal
from btc_finance_platform.p14_governor_weight_proposal import normalize_positive_scores
from btc_finance_platform.p14_governor_weight_proposal import write_governor_weight_proposal


def test_normalize_positive_scores_uses_positive_scores_only():
    rows = normalize_positive_scores(
        [
            {"expert_id": "a", "risk_adjusted_score": 0.7},
            {"expert_id": "b", "risk_adjusted_score": 0.3},
            {"expert_id": "c", "risk_adjusted_score": -0.2},
        ]
    )

    weights = {row["expert_id"]: row["proposed_weight"] for row in rows}

    assert weights["a"] == pytest.approx(0.7)
    assert weights["b"] == pytest.approx(0.3)
    assert weights["c"] == pytest.approx(0.0)


def test_normalize_positive_scores_falls_back_to_equal_weight():
    rows = normalize_positive_scores(
        [
            {"expert_id": "a", "risk_adjusted_score": -0.7},
            {"expert_id": "b", "risk_adjusted_score": -0.3},
        ]
    )

    assert rows[0]["proposed_weight"] == pytest.approx(0.5)
    assert rows[1]["proposed_weight"] == pytest.approx(0.5)


def test_meta_anomaly_guard_forces_shadow_review():
    rows = normalize_positive_scores(
        [
            {"expert_id": "a", "risk_adjusted_score": 0.7},
            {"expert_id": "b", "risk_adjusted_score": 0.3},
        ]
    )

    guarded = apply_meta_anomaly_guard(rows, "force_shadow_review")

    assert guarded["governor_mode"] == "shadow_review_only"
    assert all(row["guarded_weight"] == 0.0 for row in guarded["rows"])
    assert guarded["auto_apply_allowed"] is False


def test_governor_weight_proposal_is_review_only():
    proposal = build_governor_weight_proposal(
        [
            {"expert_id": "momentum", "regime": "trend_up", "risk_adjusted_score": 0.7},
            {"expert_id": "macro", "regime": "trend_up", "risk_adjusted_score": 0.3},
        ],
        regime="trend_up",
        meta_anomaly_status="normal",
    )

    assert proposal["proposal_status"] == "READY_FOR_OPERATOR_REVIEW"
    assert proposal["proposal_policy"]["governor_weight_auto_apply_allowed"] is False
    assert proposal["operator_review_required"] is True


def test_governor_weight_proposal_preserves_safety_boundary():
    proposal = build_governor_weight_proposal(
        [{"expert_id": "macro", "risk_adjusted_score": 0.5}],
        regime="liquidity_stress",
    )

    assert proposal["paper_only"] is True
    assert proposal["local_only"] is True
    assert proposal["real_world_actions_allowed"] is False
    assert proposal["real_order"] is False
    assert proposal["real_execution"] is False


def test_governor_weight_proposal_rejects_invalid_meta_status():
    with pytest.raises(ValueError, match="meta_anomaly_status is invalid"):
        build_governor_weight_proposal(
            [{"expert_id": "macro", "risk_adjusted_score": 0.5}],
            regime="trend_up",
            meta_anomaly_status="bad",
        )


def test_write_governor_weight_proposal_creates_json(tmp_path):
    output = tmp_path / "governor_weight_proposal.json"

    result = write_governor_weight_proposal(
        [{"expert_id": "momentum", "risk_adjusted_score": 0.8}],
        regime="trend_up",
        meta_anomaly_status="normal",
        path=output,
    )

    assert result["ok"] is True
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["type"] == "p14_governor_weight_proposal"
    assert data["proposal_policy"]["governor_weight_auto_apply_allowed"] is False
