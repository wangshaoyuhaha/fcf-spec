import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.market_snapshot import create_paper_market_snapshot


def test_create_paper_market_snapshot():
    snapshot = create_paper_market_snapshot("btcusdt", 65000)

    assert snapshot["symbol"] == "BTCUSDT"
    assert snapshot["price"] == 65000.0
    assert snapshot["source"] == "manual_paper_input"
    assert snapshot["paper_only"] is True
    assert snapshot["real_exchange_api"] is False
    assert "timestamp_utc" in snapshot


def test_market_snapshot_rejects_bad_price():
    try:
        create_paper_market_snapshot("BTCUSDT", 0)
    except ValueError as exc:
        assert "price must be positive" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_market_snapshot_rejects_missing_symbol():
    try:
        create_paper_market_snapshot("", 65000)
    except ValueError as exc:
        assert "symbol is required" in str(exc)
    else:
        raise AssertionError("expected ValueError")
