import json
import os
import sys
from pathlib import Path
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_operator_console_report import build_operator_console_markdown_report
from btc_finance_platform.paper_operator_console_report import build_operator_console_readable_summary
from btc_finance_platform.paper_operator_console_report import build_operator_console_ui_manifest
from btc_finance_platform.paper_operator_console_report import validate_operator_console_ui_manifest
from btc_finance_platform.paper_operator_console_report import write_operator_console_static_export_bundle

MULTI_MARKET_FIXTURE = Path(ROOT) / "fixtures" / "sample_multi_market_batch.json"

def test_operator_console_readable_summary_contains_workflow_counts():
    actions = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
    result = build_operator_console_readable_summary(MULTI_MARKET_FIXTURE, actions)
    assert result["ok"] is True
    assert result["type"] == "operator_console_readable_summary"
    assert result["count"] == 3
    assert result["action_counts"]["approved"] == 1
    assert result["action_counts"]["pending"] == 1
    assert result["action_counts"]["rejected"] == 1

def test_operator_console_markdown_report_contains_sections_and_notice():
    result = build_operator_console_markdown_report(MULTI_MARKET_FIXTURE)
    assert result["ok"] is True
    assert result["type"] == "operator_console_markdown_report"
    assert "# Operator Console Paper Report" in result["markdown"]
    assert "## Safety Boundary" in result["markdown"]
    assert "## Review Actions" in result["markdown"]
    assert "No real-world trading action is enabled." in result["markdown"]

def test_operator_console_ui_manifest_contains_expected_views():
    result = build_operator_console_ui_manifest(MULTI_MARKET_FIXTURE)
    assert result["ok"] is True
    assert result["type"] == "operator_console_ui_manifest"
    assert result["manifest_version"] == "p7_d7_operator_console_ui_manifest_v1"
    assert result["validation"]["ok"] is True
    view_ids = [view["view_id"] for view in result["views"]]
    assert "dashboard" in view_ids
    assert "review_queue" in view_ids
    assert "reports" in view_ids
    assert "safety" in view_ids

def test_validate_operator_console_ui_manifest_rejects_bad_type():
    with pytest.raises(ValueError, match="operator_console_ui_manifest type is invalid"):
        validate_operator_console_ui_manifest({"type": "bad"})

def test_operator_console_ui_manifest_preserves_safety_flags():
    result = build_operator_console_ui_manifest(MULTI_MARKET_FIXTURE)
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_api_key_required"] is False
    assert result["wallet_private_key_required"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True

def test_static_export_bundle_writes_expected_files(tmp_path):
    output_dir = tmp_path / "operator_console_static_export"
    result = write_operator_console_static_export_bundle(MULTI_MARKET_FIXTURE, output_dir)
    assert result["ok"] is True
    assert result["type"] == "operator_console_static_export_bundle_written"
    assert Path(result["report_file"]).exists()
    assert Path(result["manifest_file"]).exists()
    assert Path(result["bridge_file"]).exists()
    assert Path(result["summary_file"]).exists()
    saved = json.loads(Path(result["manifest_file"]).read_text(encoding="utf-8"))
    assert saved["type"] == "operator_console_ui_manifest"
    assert saved["validation"]["ok"] is True

def test_static_export_bundle_preserves_safety_flags(tmp_path):
    output_dir = tmp_path / "operator_console_static_export_safety"
    result = write_operator_console_static_export_bundle(MULTI_MARKET_FIXTURE, output_dir)
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True
