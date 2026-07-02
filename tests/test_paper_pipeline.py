import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_pipeline import (
    assert_paper_pipeline_result,
    run_paper_pipeline,
)


def test_run_paper_pipeline():
    result = run_paper_pipeline("btcusdt", 65000)

    assert result["ok"] is True
    assert result["type"] == "paper_pipeline_result"
    assert result["symbol"] == "BTCUSDT"
    assert result["mode"] == "paper"
    assert result["status"] == "WAITING_FOR_OPERATOR_REVIEW"
    assert result["action"] == "NO_LIVE_ACTION"
    assert result["paper_only"] is True
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True
    assert result["bypass_operator_review"] is False
    assert result["bypass_policy_risk_safe_boundary"] is False


def test_assert_paper_pipeline_result_passes():
    result = run_paper_pipeline("BTCUSDT", 65000)

    assert assert_paper_pipeline_result(result) is True


def test_paper_pipeline_rejects_bad_price():
    try:
        run_paper_pipeline("BTCUSDT", 0)
    except ValueError as exc:
        assert "price must be positive" in str(exc)
    else:
        raise AssertionError("expected ValueError")
