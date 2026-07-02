import os
import sys
import tempfile
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.analysis_cli import main, build_parser, run_analysis_cli


def test_analysis_cli_parser():
    parser = build_parser()
    args = parser.parse_args(["--symbol", "btcusdt", "--price", "65000", "--reference-price", "64000"])

    assert args.symbol == "btcusdt"
    assert args.price == 65000.0
    assert args.reference_price == 64000.0


def test_analysis_cli_runs_without_export(capsys):
    exit_code = main(["--symbol", "BTCUSDT", "--price", "65000", "--reference-price", "64000"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert '"type": "paper_analysis_cli_result"' in captured.out
    assert '"paper_only": true' in captured.out
    assert '"real_order": false' in captured.out
    assert '"operator_review_required": true' in captured.out


def test_analysis_cli_runs_with_export():
    parser = build_parser()

    with tempfile.TemporaryDirectory() as temp_dir:
        output = Path(temp_dir) / "report.md"
        args = parser.parse_args([
            "--symbol", "BTCUSDT",
            "--price", "65000",
            "--reference-price", "64000",
            "--output", str(output),
        ])
        result = run_analysis_cli(args)

        assert result["ok"] is True
        assert result["paper_only"] is True
        assert result["real_order"] is False
        assert result["export"]["ok"] is True
        assert output.exists()
        assert "NO_LIVE_ACTION" in output.read_text(encoding="utf-8")


def test_analysis_cli_rejects_bad_price():
    try:
        main(["--symbol", "BTCUSDT", "--price", "0", "--reference-price", "64000"])
    except ValueError as exc:
        assert "price must be positive" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_analysis_cli_rejects_bad_reference_price():
    try:
        main(["--symbol", "BTCUSDT", "--price", "65000", "--reference-price", "0"])
    except ValueError as exc:
        assert "reference_price must be positive" in str(exc)
    else:
        raise AssertionError("expected ValueError")
