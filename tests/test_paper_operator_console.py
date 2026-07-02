import json
import os
import sys
from pathlib import Path
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_operator_console import build_operator_console_contract
from btc_finance_platform.paper_operator_console import build_operator_dashboard_summary
from btc_finance_platform.paper_operator_console import build_operator_review_queue
from btc_finance_platform.paper_operator_console import build_paper_ui_safety_banner
from btc_finance_platform.paper_operator_console import build_report_viewer_index
from btc_finance_platform.paper_operator_console import validate_operator_console_contract
from btc_finance_platform.paper_operator_console import write_operator_console_bundle

MULTI_MARKET_FIXTURE = Path(ROOT) / "fixtures" / "sample_multi_market_batch.json"

def test_paper_ui_safety_banner_contains_critical_notice():
    result = build_paper_ui_safety_banner()
    assert result["ok"] is True
    assert result["type"] == "paper_ui_safety_banner"
    assert result["severity"] == "critical_safety_notice"
    assert result["paper_only"] is True

def test_operator_dashboard_summary_contains_counts_and_banner():
    result = build_operator_dashboard_summary(MULTI_MARKET_FIXTURE)
    assert result["ok"] is True
    assert result["type"] == "operator_dashboard_summary"
    assert result["count"] == 3
    assert result["safety_banner"]["type"] == "paper_ui_safety_banner"

def test_operator_review_queue_contains_three_items():
    result = build_operator_review_queue(MULTI_MARKET_FIXTURE)
    assert result["ok"] is True
    assert result["type"] == "operator_review_queue"
    assert result["queue_version"] == "p7_d2_operator_review_queue_v1"
    assert result["count"] == 3
    assert result["items"][0]["queue_id"] == "review-001"

def test_operator_review_queue_blocks_real_world_actions():
    result = build_operator_review_queue(MULTI_MARKET_FIXTURE)
    for item in result["items"]:
        assert item["real_world_actions_allowed"] is False
        assert "real_order" in item["blocked_real_world_actions"]

def test_report_viewer_index_lists_expected_reports():
    result = build_report_viewer_index(MULTI_MARKET_FIXTURE)
    assert result["ok"] is True
    assert result["type"] == "report_viewer_index"
    assert result["report_count"] == 3
    assert result["reports"][0]["paper_only"] is True

def test_operator_console_contract_has_validation():
    result = build_operator_console_contract(MULTI_MARKET_FIXTURE)
    assert result["ok"] is True
    assert result["type"] == "operator_console_contract"
    assert result["contract_version"] == "p7_d1_operator_console_contract_v1"
    assert result["validation"]["ok"] is True

def test_operator_console_contract_preserves_safety_flags():
    result = build_operator_console_contract(MULTI_MARKET_FIXTURE)
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

def test_validate_operator_console_contract_rejects_bad_type():
    with pytest.raises(ValueError, match="operator_console_contract type is invalid"):
        validate_operator_console_contract({"type": "bad"})

def test_write_operator_console_bundle(tmp_path):
    output_dir = tmp_path / "operator_console_bundle"
    result = write_operator_console_bundle(MULTI_MARKET_FIXTURE, output_dir)
    assert result["ok"] is True
    assert result["type"] == "operator_console_bundle_written"
    assert Path(result["dashboard_file"]).exists()
    assert Path(result["review_queue_file"]).exists()
    assert Path(result["report_index_file"]).exists()
    assert Path(result["contract_file"]).exists()
    saved = json.loads(Path(result["contract_file"]).read_text(encoding="utf-8"))
    assert saved["type"] == "operator_console_contract"
    assert saved["validation"]["ok"] is True
