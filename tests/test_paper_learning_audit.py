import os
import sys
from pathlib import Path
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_learning_audit import (
    build_feedback_to_calibration_handoff,
    build_learning_audit_event,
    build_learning_event_audit_trail,
    build_learning_memory_markdown_report,
    build_learning_memory_summary,
)

MULTI_MARKET_FIXTURE = Path(ROOT) / "fixtures" / "sample_multi_market_batch.json"
ACTIONS = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
OUTCOMES = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}


def test_build_learning_audit_event():
    result = build_learning_audit_event("btcusdt", "test_event", {"ok": True})
    assert result["ok"] is True
    assert result["type"] == "learning_audit_event"
    assert result["symbol"] == "BTCUSDT"
    assert result["real_world_actions_allowed"] is False


def test_build_learning_audit_event_rejects_missing_symbol():
    with pytest.raises(ValueError, match="symbol is required"):
        build_learning_audit_event("", "test_event", {})


def test_learning_event_audit_trail_records_events():
    result = build_learning_event_audit_trail(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "learning_event_audit_trail"
    assert result["event_count"] == 6


def test_feedback_to_calibration_handoff_is_not_training():
    result = build_feedback_to_calibration_handoff(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "feedback_to_calibration_handoff"
    assert result["count"] == 3
    assert result["next_phase"] == "P9 backtest and calibration"
    assert result["training_status"] == "not_trained_not_calibrated_yet"


def test_learning_memory_summary_counts():
    result = build_learning_memory_summary(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "learning_memory_summary"
    assert result["event_count"] == 6
    assert result["handoff_count"] == 3


def test_learning_memory_report_has_notice():
    result = build_learning_memory_markdown_report(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert "# Paper Learning Memory Report" in result["markdown"]
    assert "This report does not train a model." in result["markdown"]
