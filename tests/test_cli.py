import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.cli import main


def test_cli_main_runs_paper_pipeline(capsys):
    exit_code = main(["--symbol", "btcusdt", "--price", "65000"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert '"symbol": "BTCUSDT"' in captured.out
    assert '"mode": "paper"' in captured.out
    assert '"action": "NO_LIVE_ACTION"' in captured.out
    assert '"operator_review_required": true' in captured.out


def test_cli_rejects_bad_price():
    try:
        main(["--symbol", "BTCUSDT", "--price", "0"])
    except ValueError as exc:
        assert "price must be positive" in str(exc)
    else:
        raise AssertionError("expected ValueError")
