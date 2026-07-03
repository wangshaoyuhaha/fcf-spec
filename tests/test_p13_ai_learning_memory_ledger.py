import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p13_ai_learning_memory_ledger import append_learning_memory_event
from btc_finance_platform.p13_ai_learning_memory_ledger import build_learning_memory_event


def test_learning_memory_event_is_local_paper_only():
    event = build_learning_memory_event(
        "prediction_review",
        "reviewed paper-only prediction outcome",
        {"result": "paper_observation"},
    )

    assert event["learning_mode"] == "audit_and_proposal_only"
    assert event["paper_only"] is True
    assert event["local_only"] is True
    assert event["operator_review_required"] is True


def test_learning_memory_event_blocks_real_actions():
    event = build_learning_memory_event("audit", "safe audit note")

    assert event["real_world_actions_allowed"] is False
    assert event["patch_auto_apply_allowed"] is False
    assert event["trading_buttons_enabled"] is False
    assert event["real_execution"] is False
    assert event["real_money_impact"] is False


def test_learning_memory_event_rejects_sensitive_keys():
    with pytest.raises(ValueError, match="forbidden sensitive memory detected"):
        build_learning_memory_event(
            "bad_memory",
            "should reject",
            {"api_key": "do-not-store"},
        )


def test_append_learning_memory_event_creates_ledger(tmp_path):
    ledger = tmp_path / "ledger.json"

    result = append_learning_memory_event(
        ledger,
        "validation_observed",
        "local paper validation observed",
        {"pytest_passed": True},
    )

    assert result["ok"] is True
    assert result["event_count"] == 1
    assert ledger.exists()

    data = json.loads(ledger.read_text(encoding="utf-8"))
    assert data["type"] == "p13_ai_learning_memory_ledger"
    assert data["events"][0]["event_type"] == "validation_observed"


def test_append_learning_memory_event_increments_count(tmp_path):
    ledger = tmp_path / "ledger.json"

    append_learning_memory_event(ledger, "first", "first safe note")
    result = append_learning_memory_event(ledger, "second", "second safe note")

    assert result["event_count"] == 2

    data = json.loads(ledger.read_text(encoding="utf-8"))
    assert len(data["events"]) == 2
    assert data["real_world_actions_allowed"] is False
