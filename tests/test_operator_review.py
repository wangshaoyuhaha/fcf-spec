import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.decision_draft import create_paper_decision_draft
from btc_finance_platform.market_snapshot import create_paper_market_snapshot
from btc_finance_platform.operator_review import (
    assert_operator_review_gate,
    require_operator_review,
)


def test_operator_review_gate_requires_review():
    snapshot = create_paper_market_snapshot("BTCUSDT", 65000)
    draft = create_paper_decision_draft(snapshot)
    gate = require_operator_review(draft)

    assert gate["ok"] is True
    assert gate["type"] == "operator_review_gate"
    assert gate["status"] == "WAITING_FOR_OPERATOR_REVIEW"
    assert gate["action"] == "NO_LIVE_ACTION"
    assert gate["paper_only"] is True
    assert gate["operator_review_required"] is True
    assert gate["operator_approved"] is False
    assert gate["bypass_operator_review"] is False
    assert gate["real_order"] is False
    assert gate["real_execution"] is False
    assert gate["real_money_impact"] is False


def test_assert_operator_review_gate_passes():
    snapshot = create_paper_market_snapshot("BTCUSDT", 65000)
    draft = create_paper_decision_draft(snapshot)
    gate = require_operator_review(draft)

    assert assert_operator_review_gate(gate) is True


def test_operator_review_rejects_bypass():
    snapshot = create_paper_market_snapshot("BTCUSDT", 65000)
    draft = create_paper_decision_draft(snapshot)
    draft["bypass_operator_review"] = True

    try:
        require_operator_review(draft)
    except AssertionError as exc:
        assert "bypass" in str(exc)
    else:
        raise AssertionError("expected AssertionError")


def test_operator_review_rejects_real_order():
    snapshot = create_paper_market_snapshot("BTCUSDT", 65000)
    draft = create_paper_decision_draft(snapshot)
    draft["real_order"] = True

    try:
        require_operator_review(draft)
    except AssertionError as exc:
        assert "real order" in str(exc)
    else:
        raise AssertionError("expected AssertionError")
