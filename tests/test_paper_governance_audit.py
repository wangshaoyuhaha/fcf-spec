import json
import os
import sys
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_audit import build_governance_audit_event
from btc_finance_platform.paper_governance_audit import build_governance_audit_trail
from btc_finance_platform.paper_governance_audit import build_operator_approval_gate
from btc_finance_platform.paper_governance_audit import build_policy_constraint_summary
from btc_finance_platform.paper_governance_audit import require_governance_report
from btc_finance_platform.paper_governance_audit import write_governance_audit_trail
from btc_finance_platform.paper_risk_governance import build_batch_risk_governance_report


JSON_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.json"
CSV_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.csv"
SOURCES = [JSON_FIXTURE, CSV_FIXTURE]


def test_build_governance_audit_event():
    result = build_governance_audit_event("btcusdt", "test_event", {"ok": True})

    assert result["ok"] is True
    assert result["type"] == "governance_audit_event"
    assert result["symbol"] == "BTCUSDT"
    assert result["event_type"] == "test_event"
    assert result["decision"] == "audit_event_paper_only"


def test_require_governance_report_rejects_bad_type():
    with pytest.raises(ValueError, match="governance_report type is invalid"):
        require_governance_report({"ok": True, "type": "bad"})


def test_policy_constraint_summary_lists_blocked_actions():
    report = build_batch_risk_governance_report(SOURCES)
    result = build_policy_constraint_summary(report)

    assert result["ok"] is True
    assert result["type"] == "policy_constraint_summary"
    assert result["count"] == 6
    assert "real_order" in result["blocked_actions"]
    assert "automatic_live_trading" in result["blocked_actions"]


def test_operator_approval_gate_pending_waits_for_review():
    report = build_batch_risk_governance_report(SOURCES)
    result = build_operator_approval_gate(report, "pending")

    assert result["ok"] is True
    assert result["type"] == "operator_approval_gate"
    assert result["gate"] == "operator_review_pending"
    assert result["allowed_action"] == "wait_for_operator_review"
    assert result["real_world_actions_allowed"] is False


def test_operator_approval_gate_approved_still_paper_only():
    report = build_batch_risk_governance_report(SOURCES)
    result = build_operator_approval_gate(report, "approved")

    assert result["ok"] is True
    assert result["operator_status"] == "approved"
    assert result["real_world_actions_allowed"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False


def test_operator_approval_gate_rejects_invalid_status():
    report = build_batch_risk_governance_report(SOURCES)

    with pytest.raises(ValueError, match="operator_status must be pending, approved, or rejected"):
        build_operator_approval_gate(report, "live")


def test_build_governance_audit_trail_records_governor_and_policy_events():
    result = build_governance_audit_trail(SOURCES)

    assert result["ok"] is True
    assert result["type"] == "governance_audit_trail"
    assert result["event_count"] == 12
    assert result["constraint_summary"]["ok"] is True
    assert result["operator_gate"]["gate"] == "operator_review_pending"


def test_governance_audit_trail_preserves_safety_flags():
    result = build_governance_audit_trail(SOURCES)

    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_api_key_required"] is False
    assert result["wallet_private_key_required"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_balance"] is False
    assert result["real_position"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True


def test_write_governance_audit_trail(tmp_path):
    output = tmp_path / "audit" / "governance_audit_trail.json"
    result = write_governance_audit_trail(SOURCES, output)

    assert result["ok"] is True
    assert result["type"] == "governance_audit_trail_written"
    assert output.exists()

    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["type"] == "governance_audit_trail"
    assert saved["ok"] is True
