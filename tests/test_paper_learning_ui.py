import json
import os
import sys
from pathlib import Path
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_learning_ui import build_learning_dataset_index
from btc_finance_platform.paper_learning_ui import build_learning_memory_ui_card
from btc_finance_platform.paper_learning_ui import build_learning_memory_ui_contract
from btc_finance_platform.paper_learning_ui import build_learning_memory_ui_manifest
from btc_finance_platform.paper_learning_ui import validate_learning_memory_ui_contract
from btc_finance_platform.paper_learning_ui import validate_learning_memory_ui_manifest
from btc_finance_platform.paper_learning_ui import write_learning_memory_ui_bundle

MULTI_MARKET_FIXTURE = Path(ROOT) / "fixtures" / "sample_multi_market_batch.json"
ACTIONS = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
OUTCOMES = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}

def test_learning_memory_ui_card_maps_outcome_to_display_status():
    row = {
        "symbol": "BTCUSDT",
        "asset_class": "crypto",
        "market": "paper_binance",
        "paper_signal": "paper_review_only",
        "risk_level": "low",
        "risk_score": 1,
        "operator_action": "approved",
        "paper_outcome_status": "paper_success",
        "calibration_use": "future_offline_backtest_and_calibration_only",
    }
    result = build_learning_memory_ui_card(row)
    assert result["ok"] is True
    assert result["type"] == "learning_memory_ui_card"
    assert result["display_status"] == "paper_success_recorded"
    assert result["training_status"] == "not_trained_not_calibrated_yet"

def test_learning_memory_ui_contract_has_validation():
    result = build_learning_memory_ui_contract(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "learning_memory_ui_contract"
    assert result["count"] == 3
    assert result["validation"]["ok"] is True

def test_learning_memory_ui_contract_preserves_safety_flags():
    result = build_learning_memory_ui_contract(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True

def test_validate_learning_memory_ui_contract_rejects_bad_type():
    with pytest.raises(ValueError, match="learning_memory_ui_contract type is invalid"):
        validate_learning_memory_ui_contract({"type": "bad"})

def test_learning_dataset_index_groups_by_outcome_and_action():
    result = build_learning_dataset_index(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "learning_dataset_index"
    assert "BTCUSDT" in result["by_symbol"]
    assert result["by_outcome"]["paper_success"] == ["BTCUSDT"]
    assert result["by_action"]["approved"] == ["BTCUSDT"]

def test_learning_memory_ui_manifest_contains_expected_views():
    result = build_learning_memory_ui_manifest(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "learning_memory_ui_manifest"
    assert result["validation"]["ok"] is True
    view_ids = [view["view_id"] for view in result["views"]]
    assert "learning_summary" in view_ids
    assert "feedback_dataset" in view_ids
    assert "calibration_handoff" in view_ids

def test_validate_learning_memory_ui_manifest_rejects_bad_type():
    with pytest.raises(ValueError, match="learning_memory_ui_manifest type is invalid"):
        validate_learning_memory_ui_manifest({"type": "bad"})

def test_write_learning_memory_ui_bundle(tmp_path):
    output_dir = tmp_path / "learning_ui_bundle"
    result = write_learning_memory_ui_bundle(MULTI_MARKET_FIXTURE, output_dir, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "learning_memory_ui_bundle_written"
    assert Path(result["contract_file"]).exists()
    assert Path(result["index_file"]).exists()
    assert Path(result["manifest_file"]).exists()
    assert Path(result["report_file"]).exists()
    saved = json.loads(Path(result["manifest_file"]).read_text(encoding="utf-8"))
    assert saved["type"] == "learning_memory_ui_manifest"
    assert saved["validation"]["ok"] is True
