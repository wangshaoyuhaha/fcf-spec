import json
import os
import sys
from pathlib import Path
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_multi_market_pipeline import build_multi_market_pipeline_report_from_json
from btc_finance_platform.paper_multi_market_report import build_multi_market_markdown_report
from btc_finance_platform.paper_multi_market_report import build_multi_market_report_summary
from btc_finance_platform.paper_multi_market_report import build_multi_market_ui_card
from btc_finance_platform.paper_multi_market_report import build_multi_market_ui_contract
from btc_finance_platform.paper_multi_market_report import require_multi_market_pipeline_report
from btc_finance_platform.paper_multi_market_report import validate_multi_market_ui_contract
from btc_finance_platform.paper_multi_market_report import write_multi_market_report_bundle

MULTI_MARKET_FIXTURE = Path(ROOT) / "fixtures" / "sample_multi_market_batch.json"

def test_require_multi_market_pipeline_report_rejects_bad_type():
    with pytest.raises(ValueError, match="multi_market_pipeline_report type is invalid"):
        require_multi_market_pipeline_report({"ok": True, "type": "bad"})

def test_multi_market_report_summary():
    result = build_multi_market_report_summary(MULTI_MARKET_FIXTURE)
    assert result["ok"] is True
    assert result["type"] == "multi_market_report_summary"
    assert result["count"] == 3
    assert result["asset_class_counts"]["crypto"] == 1
    assert result["asset_class_counts"]["stock"] == 1

def test_build_multi_market_ui_card_contains_asset_class_and_market():
    pipeline = build_multi_market_pipeline_report_from_json(MULTI_MARKET_FIXTURE)
    market_item = pipeline["pipeline"]["loaded_contract"]["contract"]["items"][0]
    governor = pipeline["governance"]["governor_decisions"][0]
    policy = pipeline["governance"]["policy_gates"][0]
    card = build_multi_market_ui_card(market_item, governor, policy)
    assert card["ok"] is True
    assert card["type"] == "multi_market_ui_card"
    assert card["symbol"] == "BTCUSDT"
    assert card["asset_class"] == "crypto"
    assert card["market"] == "paper_binance"

def test_build_multi_market_ui_contract_has_validation():
    result = build_multi_market_ui_contract(MULTI_MARKET_FIXTURE)
    assert result["ok"] is True
    assert result["type"] == "multi_market_ui_contract"
    assert result["contract_version"] == "p6_d7_multi_market_ui_contract_v1"
    assert result["count"] == 3
    assert len(result["cards"]) == 3
    assert result["validation"]["ok"] is True

def test_validate_multi_market_ui_contract_rejects_bad_type():
    with pytest.raises(ValueError, match="multi_market_ui_contract type is invalid"):
        validate_multi_market_ui_contract({"type": "bad"})

def test_multi_market_ui_contract_preserves_safety_flags():
    result = build_multi_market_ui_contract(MULTI_MARKET_FIXTURE)
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_api_key_required"] is False
    assert result["wallet_private_key_required"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True

def test_multi_market_markdown_report_contains_sections():
    result = build_multi_market_markdown_report(MULTI_MARKET_FIXTURE)
    assert result["ok"] is True
    assert result["type"] == "multi_market_markdown_report"
    assert "# Multi-Market Paper Report" in result["markdown"]
    assert "## Safety Boundary" in result["markdown"]
    assert "## Cards" in result["markdown"]
    assert "Stocks, ETFs, and crypto entries are paper-only contract inputs." in result["markdown"]

def test_write_multi_market_report_bundle(tmp_path):
    output_dir = tmp_path / "multi_market_bundle"
    result = write_multi_market_report_bundle(MULTI_MARKET_FIXTURE, output_dir)
    assert result["ok"] is True
    assert result["type"] == "multi_market_report_bundle_written"
    assert Path(result["markdown_file"]).exists()
    assert Path(result["contract_file"]).exists()
    assert Path(result["summary_file"]).exists()
    saved = json.loads(Path(result["contract_file"]).read_text(encoding="utf-8"))
    assert saved["type"] == "multi_market_ui_contract"
    assert saved["validation"]["ok"] is True
