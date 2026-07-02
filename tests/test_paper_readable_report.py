import json
import os
import sys
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_readable_report import build_paper_analysis_markdown_report
from btc_finance_platform.paper_readable_report import build_paper_report_summary
from btc_finance_platform.paper_readable_report import build_symbol_markdown_section
from btc_finance_platform.paper_readable_report import write_paper_analysis_markdown_report
from btc_finance_platform.paper_readable_report import write_paper_analysis_report_bundle
from btc_finance_platform.paper_review_packet import build_paper_analysis_review_packet


JSON_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.json"
CSV_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.csv"
SOURCES = [JSON_FIXTURE, CSV_FIXTURE]


def test_build_paper_report_summary_from_review_packet():
    packet = build_paper_analysis_review_packet(SOURCES)
    result = build_paper_report_summary(packet)

    assert result["ok"] is True
    assert result["type"] == "paper_report_summary"
    assert result["count"] == 6
    assert result["requires_operator_review"] is True
    assert result["decision"] == "summary_only_no_real_trade"


def test_build_symbol_markdown_section_contains_review_fields():
    packet = build_paper_analysis_review_packet(SOURCES)
    section = build_symbol_markdown_section(packet["review_items"][0])

    assert "### BTCUSDT" in section
    assert "Priority:" in section
    assert "Signal:" in section
    assert "Risk level:" in section
    assert "Operator action:" in section


def test_build_paper_analysis_markdown_report_contains_summary_and_notice():
    result = build_paper_analysis_markdown_report(SOURCES)

    assert result["ok"] is True
    assert result["type"] == "paper_analysis_markdown_report"
    assert "# Paper Analysis Report" in result["markdown"]
    assert "## Safety Boundary" in result["markdown"]
    assert "## Review Items" in result["markdown"]
    assert "This report is not financial advice." in result["markdown"]


def test_paper_analysis_markdown_report_preserves_safety_flags():
    result = build_paper_analysis_markdown_report(SOURCES)

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


def test_write_paper_analysis_markdown_report(tmp_path):
    output = tmp_path / "paper_analysis_report.md"
    result = write_paper_analysis_markdown_report(SOURCES, output)

    assert result["ok"] is True
    assert result["type"] == "paper_analysis_markdown_report_written"
    assert output.exists()
    assert "# Paper Analysis Report" in output.read_text(encoding="utf-8")


def test_write_paper_analysis_report_bundle(tmp_path):
    output_dir = tmp_path / "bundle"
    result = write_paper_analysis_report_bundle(SOURCES, output_dir)

    assert result["ok"] is True
    assert result["type"] == "paper_analysis_report_bundle_written"
    assert Path(result["markdown_file"]).exists()
    assert Path(result["json_file"]).exists()

    saved = json.loads(Path(result["json_file"]).read_text(encoding="utf-8"))
    assert saved["type"] == "paper_analysis_markdown_report"
    assert saved["ok"] is True


def test_report_summary_rejects_bad_packet():
    with pytest.raises(ValueError, match="review_packet type is invalid"):
        build_paper_report_summary({"ok": True, "type": "bad"})
