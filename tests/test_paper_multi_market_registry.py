import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_multi_market_registry import build_multi_market_adapter_registry
from btc_finance_platform.paper_multi_market_registry import build_multi_market_readiness_bundle
from btc_finance_platform.paper_multi_market_registry import build_multi_market_readiness_gate
from btc_finance_platform.paper_multi_market_registry import write_multi_market_readiness_bundle

MULTI_MARKET_FIXTURE = Path(ROOT) / "fixtures" / "sample_multi_market_batch.json"

def test_multi_market_adapter_registry_contains_expected_asset_classes():
    result = build_multi_market_adapter_registry()
    assert result["ok"] is True
    assert result["type"] == "multi_market_adapter_registry"
    assert result["registry_version"] == "p6_d10_adapter_registry_v1"
    assert "crypto" in result["asset_classes"]
    assert "stock" in result["asset_classes"]
    assert "etf" in result["asset_classes"]

def test_adapter_registry_is_paper_only_and_blocks_real_connections():
    result = build_multi_market_adapter_registry()
    for item in result["registry"].values():
        assert item["adapter_status"] == "paper_contract_only"
        assert item["real_connection_enabled"] is False
        assert item["real_brokerage_enabled"] is False
        assert item["real_exchange_enabled"] is False
        assert "real_order" in item["blocked_actions"]

def test_multi_market_readiness_gate_passes_for_fixture():
    result = build_multi_market_readiness_gate(MULTI_MARKET_FIXTURE)
    assert result["ok"] is True
    assert result["type"] == "multi_market_readiness_gate"
    assert result["gate"] == "pass"
    assert result["count"] == 3
    assert all(result["checks"].values())

def test_multi_market_readiness_gate_preserves_safety_flags():
    result = build_multi_market_readiness_gate(MULTI_MARKET_FIXTURE)
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_api_key_required"] is False
    assert result["wallet_private_key_required"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True

def test_multi_market_readiness_bundle_contains_contract_registry_and_gate():
    result = build_multi_market_readiness_bundle(MULTI_MARKET_FIXTURE)
    assert result["ok"] is True
    assert result["type"] == "multi_market_readiness_bundle"
    assert result["contract"]["type"] == "multi_market_ui_contract"
    assert result["adapter_registry"]["type"] == "multi_market_adapter_registry"
    assert result["readiness_gate"]["type"] == "multi_market_readiness_gate"
    assert result["next_step"] == "P6 closeout before any further expansion"

def test_multi_market_readiness_bundle_preserves_safety_flags():
    result = build_multi_market_readiness_bundle(MULTI_MARKET_FIXTURE)
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True

def test_write_multi_market_readiness_bundle(tmp_path):
    output_dir = tmp_path / "readiness_bundle"
    result = write_multi_market_readiness_bundle(MULTI_MARKET_FIXTURE, output_dir)
    assert result["ok"] is True
    assert result["type"] == "multi_market_readiness_bundle_written"
    assert Path(result["bundle_file"]).exists()
    assert Path(result["registry_file"]).exists()
    assert Path(result["gate_file"]).exists()
    saved = json.loads(Path(result["bundle_file"]).read_text(encoding="utf-8"))
    assert saved["type"] == "multi_market_readiness_bundle"
    assert saved["readiness_gate"]["gate"] == "pass"

def test_readiness_bundle_registry_has_no_real_integration_enabled():
    result = build_multi_market_readiness_bundle(MULTI_MARKET_FIXTURE)
    for item in result["adapter_registry"]["registry"].values():
        assert item["real_connection_enabled"] is False
        assert item["real_brokerage_enabled"] is False
        assert item["real_exchange_enabled"] is False
