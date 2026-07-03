import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_shadow_ledger import append_shadow_ledger_event
from btc_finance_platform.p14_shadow_ledger import build_shadow_ledger_event
from btc_finance_platform.p14_shadow_ledger import summarize_shadow_ledger


def sample_proposals():
    return [
        {
            "expert_id": "macro_expert",
            "direction": "observe",
            "confidence": 0.55,
        },
        {
            "expert_id": "momentum_expert",
            "direction": "long",
            "confidence": 0.72,
        },
    ]


def test_shadow_ledger_event_records_all_expert_proposals():
    event = build_shadow_ledger_event(
        "decision_001",
        "trend_up",
        sample_proposals(),
        selected_expert_id="momentum_expert",
    )

    assert event["type"] == "p14_shadow_ledger_event"
    assert event["proposal_count"] == 2
    assert event["selected_expert_id"] == "momentum_expert"
    assert event["counterfactual_learning_enabled"] is True


def test_shadow_ledger_event_preserves_paper_only_boundary():
    event = build_shadow_ledger_event("decision_001", "trend_up", sample_proposals())

    assert event["paper_only"] is True
    assert event["local_only"] is True
    assert event["operator_review_required"] is True
    assert event["real_world_actions_allowed"] is False
    assert event["real_order"] is False
    assert event["real_execution"] is False


def test_shadow_ledger_rejects_invalid_confidence():
    with pytest.raises(ValueError, match="confidence must be between 0 and 1"):
        build_shadow_ledger_event(
            "decision_001",
            "trend_up",
            [{"expert_id": "bad", "direction": "long", "confidence": 1.5}],
        )


def test_shadow_ledger_rejects_sensitive_fields():
    with pytest.raises(ValueError, match="forbidden sensitive field detected"):
        build_shadow_ledger_event(
            "decision_001",
            "trend_up",
            [{"expert_id": "bad", "direction": "long", "confidence": 0.5, "api_key": "never"}],
        )


def test_append_shadow_ledger_event_creates_ledger(tmp_path):
    ledger = tmp_path / "shadow_ledger.json"

    result = append_shadow_ledger_event(
        ledger,
        "decision_001",
        "trend_up",
        sample_proposals(),
        selected_expert_id="macro_expert",
    )

    assert result["ok"] is True
    assert result["event_count"] == 1
    assert ledger.exists()

    data = json.loads(ledger.read_text(encoding="utf-8"))
    assert data["type"] == "p14_shadow_ledger"
    assert data["events"][0]["regime"] == "trend_up"


def test_summarize_shadow_ledger_counts_regime_and_experts(tmp_path):
    ledger = tmp_path / "shadow_ledger.json"

    append_shadow_ledger_event(ledger, "decision_001", "trend_up", sample_proposals())
    summary = summarize_shadow_ledger(ledger)

    assert summary["event_count"] == 1
    assert summary["regime_counts"]["trend_up"] == 1
    assert summary["expert_counts"]["macro_expert"] == 1
    assert summary["expert_counts"]["momentum_expert"] == 1
    assert summary["real_world_actions_allowed"] is False
