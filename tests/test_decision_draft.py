import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.decision_draft import (
    assert_paper_decision_draft,
    create_paper_decision_draft,
)
from btc_finance_platform.market_snapshot import create_paper_market_snapshot


def test_create_paper_decision_draft():
    snapshot = create_paper_market_snapshot("BTCUSDT", 65000)
    draft = create_paper_decision_draft(snapshot)

    assert draft["ok"] is True
    assert draft["type"] == "paper_decision_draft"
    assert draft["symbol"] == "BTCUSDT"
    assert draft["reference_price"] == 65000.0
    assert draft["status"] == "REVIEW_REQUIRED"
    assert draft["action"] == "NO_LIVE_ACTION"
    assert draft["paper_only"] is True
    assert draft["real_order"] is False
    assert draft["real_execution"] is False
    assert draft["real_money_impact"] is False
    assert draft["operator_review_required"] is True
    assert draft["bypass_operator_review"] is False
    assert draft["bypass_policy_risk_safe_boundary"] is False


def test_assert_paper_decision_draft_passes():
    snapshot = create_paper_market_snapshot("BTCUSDT", 65000)
    draft = create_paper_decision_draft(snapshot)

    assert assert_paper_decision_draft(draft) is True


def test_decision_draft_rejects_non_paper_snapshot():
    snapshot = create_paper_market_snapshot("BTCUSDT", 65000)
    snapshot["paper_only"] = False

    try:
        create_paper_decision_draft(snapshot)
    except AssertionError as exc:
        assert "paper-only snapshot" in str(exc)
    else:
        raise AssertionError("expected AssertionError")


def test_decision_draft_rejects_real_exchange_snapshot():
    snapshot = create_paper_market_snapshot("BTCUSDT", 65000)
    snapshot["real_exchange_api"] = True

    try:
        create_paper_decision_draft(snapshot)
    except AssertionError as exc:
        assert "real exchange API" in str(exc)
    else:
        raise AssertionError("expected AssertionError")
