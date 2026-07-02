import json
import os
import sys
from pathlib import Path
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_multi_market_pipeline import build_multi_market_contract_from_json
from btc_finance_platform.paper_multi_market_pipeline import build_multi_market_governance_summary_from_analysis
from btc_finance_platform.paper_multi_market_pipeline import build_multi_market_pipeline_report_from_json
from btc_finance_platform.paper_multi_market_pipeline import load_multi_market_json_items
from btc_finance_platform.paper_multi_market_pipeline import run_multi_market_paper_analysis_from_contract
from btc_finance_platform.paper_multi_market_pipeline import run_multi_market_paper_analysis_from_json
from btc_finance_platform.paper_multi_market_pipeline import write_multi_market_pipeline_report

MULTI_MARKET_FIXTURE = Path(ROOT) / "fixtures" / "sample_multi_market_batch.json"

def test_load_multi_market_json_items_from_fixture():
    result = load_multi_market_json_items(MULTI_MARKET_FIXTURE)
    assert isinstance(result, list)
    assert len(result) == 3
    assert result[0]["asset_class"] == "crypto"

def test_build_multi_market_contract_from_json():
    result = build_multi_market_contract_from_json(MULTI_MARKET_FIXTURE)
    assert result["ok"] is True
    assert result["type"] == "multi_market_contract_from_json"
    assert result["count"] == 3
    assert result["symbols"] == ["BTCUSDT", "AAPL", "SPY"]
    assert result["asset_class_counts"]["stock"] == 1

def test_run_multi_market_paper_analysis_from_contract():
    loaded = build_multi_market_contract_from_json(MULTI_MARKET_FIXTURE)
    result = run_multi_market_paper_analysis_from_contract(loaded["contract"])
    assert result["ok"] is True
    assert result["type"] == "multi_market_paper_analysis_result"
    assert result["count"] == 3
    assert result["analysis"]["type"] == "paper_batch_analysis_baseline"

def test_run_multi_market_paper_analysis_from_json():
    result = run_multi_market_paper_analysis_from_json(MULTI_MARKET_FIXTURE)
    assert result["ok"] is True
    assert result["type"] == "multi_market_json_to_paper_analysis"
    assert result["count"] == 3
    assert result["asset_class_counts"]["crypto"] == 1

def test_multi_market_governance_summary_from_analysis():
    pipeline = run_multi_market_paper_analysis_from_json(MULTI_MARKET_FIXTURE)
    result = build_multi_market_governance_summary_from_analysis(pipeline["analysis_result"])
    assert result["ok"] is True
    assert result["type"] == "multi_market_governance_summary"
    assert result["count"] == 3
    assert len(result["governor_decisions"]) == 3
    assert len(result["policy_gates"]) == 3

def test_multi_market_pipeline_report_from_json():
    result = build_multi_market_pipeline_report_from_json(MULTI_MARKET_FIXTURE)
    assert result["ok"] is True
    assert result["type"] == "multi_market_pipeline_report"
    assert result["count"] == 3
    assert result["pipeline"]["type"] == "multi_market_json_to_paper_analysis"
    assert result["governance"]["type"] == "multi_market_governance_summary"

def test_multi_market_pipeline_preserves_safety_flags():
    result = build_multi_market_pipeline_report_from_json(MULTI_MARKET_FIXTURE)
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_api_key_required"] is False
    assert result["wallet_private_key_required"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_balance"] is False
    assert result["real_position"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True

def test_write_multi_market_pipeline_report(tmp_path):
    output = tmp_path / "multi_market" / "pipeline_report.json"
    result = write_multi_market_pipeline_report(MULTI_MARKET_FIXTURE, output)
    assert result["ok"] is True
    assert result["type"] == "multi_market_pipeline_report_written"
    assert output.exists()
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["type"] == "multi_market_pipeline_report"
    assert saved["ok"] is True

def test_load_multi_market_json_items_rejects_empty_file(tmp_path):
    bad_file = tmp_path / "empty.json"
    bad_file.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="multi-market json must not be empty"):
        load_multi_market_json_items(bad_file)
