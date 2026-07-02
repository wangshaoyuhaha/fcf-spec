import json
import os
import sys
from pathlib import Path
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_operator_console_acceptance import build_operator_console_acceptance_summary
from btc_finance_platform.paper_operator_console_acceptance import build_operator_console_page_registry
from btc_finance_platform.paper_operator_console_acceptance import build_operator_console_ui_acceptance_gate
from btc_finance_platform.paper_operator_console_acceptance import validate_operator_console_page_registry
from btc_finance_platform.paper_operator_console_acceptance import write_operator_console_acceptance_bundle

MULTI_MARKET_FIXTURE = Path(ROOT) / "fixtures" / "sample_multi_market_batch.json"

def test_operator_console_page_registry_contains_expected_pages():
    result = build_operator_console_page_registry(MULTI_MARKET_FIXTURE)
    assert result["ok"] is True
    assert result["type"] == "operator_console_page_registry"
    assert result["registry_version"] == "p7_d10_operator_console_page_registry_v1"
    assert "dashboard" in result["page_ids"]
    assert "review_queue" in result["page_ids"]
    assert "reports" in result["page_ids"]
    assert "safety" in result["page_ids"]

def test_operator_console_page_registry_validation_passes():
    registry = build_operator_console_page_registry(MULTI_MARKET_FIXTURE)
    result = validate_operator_console_page_registry(registry)
    assert result["ok"] is True
    assert result["type"] == "operator_console_page_registry_validation"
    assert all(result["checks"].values())

def test_operator_console_page_registry_validation_rejects_bad_type():
    with pytest.raises(ValueError, match="operator_console_page_registry type is invalid"):
        validate_operator_console_page_registry({"type": "bad"})

def test_operator_console_ui_acceptance_gate_passes():
    result = build_operator_console_ui_acceptance_gate(MULTI_MARKET_FIXTURE)
    assert result["ok"] is True
    assert result["type"] == "operator_console_ui_acceptance_gate"
    assert result["gate"] == "pass"
    assert "dashboard" in result["page_ids"]

def test_operator_console_ui_acceptance_gate_preserves_safety_flags():
    result = build_operator_console_ui_acceptance_gate(MULTI_MARKET_FIXTURE)
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_api_key_required"] is False
    assert result["wallet_private_key_required"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True

def test_operator_console_acceptance_summary_accepts_for_static_ui_handoff():
    result = build_operator_console_acceptance_summary(MULTI_MARKET_FIXTURE)
    assert result["ok"] is True
    assert result["type"] == "operator_console_acceptance_summary"
    assert result["gate"] == "pass"
    assert result["accepted_for"] == "future_static_ui_handoff"
    assert result["real_world_actions_allowed"] is False

def test_operator_console_acceptance_bundle_writes_expected_files(tmp_path):
    output_dir = tmp_path / "operator_console_acceptance_bundle"
    result = write_operator_console_acceptance_bundle(MULTI_MARKET_FIXTURE, output_dir)
    assert result["ok"] is True
    assert result["type"] == "operator_console_acceptance_bundle_written"
    assert Path(result["registry_file"]).exists()
    assert Path(result["gate_file"]).exists()
    assert Path(result["summary_file"]).exists()
    assert Path(result["report_file"]).exists()
    saved = json.loads(Path(result["gate_file"]).read_text(encoding="utf-8"))
    assert saved["type"] == "operator_console_ui_acceptance_gate"
    assert saved["gate"] == "pass"

def test_operator_console_acceptance_bundle_preserves_safety_flags(tmp_path):
    output_dir = tmp_path / "operator_console_acceptance_bundle_safety"
    result = write_operator_console_acceptance_bundle(MULTI_MARKET_FIXTURE, output_dir)
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True
