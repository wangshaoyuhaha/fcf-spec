import json
import os
import sys
from pathlib import Path
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_model_registry_ui import (
    build_model_registry_ui_contract,
    build_model_registry_ui_manifest,
    build_model_version_index,
    validate_model_registry_ui_contract,
    write_model_registry_ui_bundle,
)

MULTI_MARKET_FIXTURE = Path(ROOT) / "fixtures" / "sample_multi_market_batch.json"
ACTIONS = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
OUTCOMES = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}


def test_model_version_index_builds():
    result = build_model_version_index(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "model_version_index"
    assert result["count"] == 1
    assert result["deployment_status"] == "not_deployed"


def test_model_registry_ui_contract_validates():
    result = build_model_registry_ui_contract(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "model_registry_ui_contract"
    assert result["validation"]["ok"] is True
    assert result["card_count"] == 1


def test_model_registry_ui_contract_has_views():
    result = build_model_registry_ui_contract(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    view_ids = [view["view_id"] for view in result["views"]]
    assert "model_versions" in view_ids
    assert "approval_gates" in view_ids
    assert "model_registry_report" in view_ids
    assert "safety" in view_ids


def test_model_registry_ui_blocks_live_actions():
    result = build_model_registry_ui_contract(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["deployment_allowed_now"] is False
    assert result["parameter_update_allowed_now"] is False
    assert result["real_world_actions_allowed"] is False
    assert all(card["real_world_actions_allowed"] is False for card in result["cards"])


def test_validate_model_registry_ui_contract_rejects_bad_type():
    with pytest.raises(ValueError, match="model_registry_ui_contract type is invalid"):
        validate_model_registry_ui_contract({"type": "bad"})


def test_model_registry_ui_manifest_builds():
    result = build_model_registry_ui_manifest(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "model_registry_ui_manifest"
    assert result["model_count"] == 1
    assert result["real_world_actions_allowed"] is False


def test_write_model_registry_ui_bundle(tmp_path):
    output_dir = tmp_path / "model_registry_ui_bundle"
    result = write_model_registry_ui_bundle(MULTI_MARKET_FIXTURE, output_dir, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert Path(result["index_file"]).exists()
    assert Path(result["ui_file"]).exists()
    assert Path(result["manifest_file"]).exists()
    saved = json.loads(Path(result["manifest_file"]).read_text(encoding="utf-8"))
    assert saved["type"] == "model_registry_ui_manifest"


def test_written_model_registry_ui_bundle_preserves_safety(tmp_path):
    output_dir = tmp_path / "model_registry_ui_bundle_safety"
    result = write_model_registry_ui_bundle(MULTI_MARKET_FIXTURE, output_dir, ACTIONS, OUTCOMES)
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
