import os
import sys
import tempfile
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.analysis_flow import run_paper_analysis_flow
from btc_finance_platform.paper_run_record import assert_paper_run_record
from btc_finance_platform.report_exporter import export_paper_report


def test_paper_analysis_flow_result():
    result = run_paper_analysis_flow({
        "symbol": "btcusdt",
        "price": 65000,
        "reference_price": 64000,
    })

    assert result["ok"] is True
    assert result["type"] == "paper_analysis_flow_result"
    assert result["paper_only"] is True
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["operator_review_required"] is True
    assert result["analysis"]["symbol"] == "BTCUSDT"
    assert "NO_LIVE_ACTION" in result["report"]


def test_paper_run_record_assertion():
    result = run_paper_analysis_flow({
        "symbol": "BTCUSDT",
        "price": 65000,
        "reference_price": 64000,
    })

    assert assert_paper_run_record(result["record"]) is True
    assert result["record"]["real_money_impact"] is False


def test_report_exporter_writes_file():
    result = run_paper_analysis_flow({
        "symbol": "BTCUSDT",
        "price": 65000,
        "reference_price": 64000,
    })

    with tempfile.TemporaryDirectory() as temp_dir:
        output = Path(temp_dir) / "paper_report.md"
        exported = export_paper_report(result["report"], str(output))

        assert exported["ok"] is True
        assert exported["paper_only"] is True
        assert exported["real_order"] is False
        assert output.exists()
        assert "NO_LIVE_ACTION" in output.read_text(encoding="utf-8")


def test_report_exporter_rejects_live_like_report():
    try:
        export_paper_report("bad report", "unused.md")
    except AssertionError as exc:
        assert "NO_LIVE_ACTION" in str(exc)
    else:
        raise AssertionError("expected AssertionError")


def test_analysis_flow_rejects_bad_payload():
    try:
        run_paper_analysis_flow({"symbol": "BTCUSDT", "price": 0})
    except ValueError as exc:
        assert "price must be positive" in str(exc)
    else:
        raise AssertionError("expected ValueError")
