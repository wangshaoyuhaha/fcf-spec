import json
import os
import sys
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.local_data_handoff import build_local_analysis_handoff_package
from btc_finance_platform.paper_analysis_pipeline import build_paper_analysis_pipeline_report
from btc_finance_platform.paper_analysis_pipeline import extract_analysis_items_from_handoff
from btc_finance_platform.paper_analysis_pipeline import run_paper_analysis_from_handoff_package
from btc_finance_platform.paper_analysis_pipeline import run_paper_analysis_from_local_files
from btc_finance_platform.paper_analysis_pipeline import write_paper_analysis_pipeline_report


JSON_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.json"
CSV_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.csv"
SOURCES = [JSON_FIXTURE, CSV_FIXTURE]


def test_extract_analysis_items_from_handoff_package():
    handoff = build_local_analysis_handoff_package(SOURCES)
    items = extract_analysis_items_from_handoff(handoff)

    assert len(items) == 6
    assert items[0]["symbol"] == "BTCUSDT"
    assert set(items[0].keys()) == {"symbol", "price", "reference_price"}


def test_run_paper_analysis_from_handoff_package():
    handoff = build_local_analysis_handoff_package(SOURCES)
    result = run_paper_analysis_from_handoff_package(handoff)

    assert result["ok"] is True
    assert result["type"] == "paper_analysis_from_handoff_package"
    assert result["handoff_gate"] == "pass"
    assert result["count"] == 6
    assert result["decision"] == "paper_analysis_only_no_real_trade"


def test_run_paper_analysis_from_local_files_connects_p3_to_p4():
    result = run_paper_analysis_from_local_files(SOURCES)

    assert result["ok"] is True
    assert result["type"] == "paper_analysis_from_local_files"
    assert result["handoff_package"]["type"] == "local_analysis_handoff_package"
    assert result["pipeline_result"]["type"] == "paper_analysis_from_handoff_package"
    assert result["count"] == 6


def test_paper_analysis_pipeline_report_summarizes_risk_and_signals():
    result = build_paper_analysis_pipeline_report(SOURCES)

    assert result["ok"] is True
    assert result["type"] == "paper_analysis_pipeline_report"
    assert result["count"] == 6
    assert isinstance(result["risk_levels"], dict)
    assert isinstance(result["signals"], dict)
    assert result["decision"] == "report_only_no_real_trade"


def test_paper_analysis_pipeline_preserves_safety_flags():
    result = build_paper_analysis_pipeline_report(SOURCES)

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


def test_write_paper_analysis_pipeline_report(tmp_path):
    output = tmp_path / "reports" / "paper_analysis_pipeline_report.json"
    result = write_paper_analysis_pipeline_report(SOURCES, output)

    assert result["ok"] is True
    assert result["type"] == "paper_analysis_pipeline_report_written"
    assert output.exists()

    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["type"] == "paper_analysis_pipeline_report"
    assert saved["ok"] is True


def test_pipeline_rejects_failed_handoff_gate():
    handoff = build_local_analysis_handoff_package(SOURCES)
    handoff["gate"] = "fail"

    with pytest.raises(ValueError, match="handoff_package gate must pass"):
        run_paper_analysis_from_handoff_package(handoff)
