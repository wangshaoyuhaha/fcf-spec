import json
import os
import sys
from pathlib import Path
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_learning_memory import build_learning_memory_schema
from btc_finance_platform.paper_learning_memory import build_operator_feedback_dataset
from btc_finance_platform.paper_learning_memory import build_paper_outcome_tracking_contract
from btc_finance_platform.paper_learning_memory import normalize_paper_outcome_status
from btc_finance_platform.paper_learning_memory import validate_operator_feedback_dataset
from btc_finance_platform.paper_learning_memory import write_learning_memory_bundle

MULTI_MARKET_FIXTURE = Path(ROOT) / "fixtures" / "sample_multi_market_batch.json"

def test_learning_memory_schema_contains_required_fields():
    result = build_learning_memory_schema()
    assert result["ok"] is True
    assert result["type"] == "learning_memory_schema"
    assert "memory_id" in result["required_fields"]
    assert "paper_outcome_status" in result["required_fields"]
    assert result["decision"] == "schema_only_no_training_no_real_trade"

def test_normalize_paper_outcome_status_rejects_invalid_status():
    with pytest.raises(ValueError, match="paper outcome status is invalid"):
        normalize_paper_outcome_status("live_profit")

def test_operator_feedback_dataset_records_actions_and_outcomes():
    actions = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
    outcomes = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}
    result = build_operator_feedback_dataset(MULTI_MARKET_FIXTURE, actions, outcomes)
    assert result["ok"] is True
    assert result["type"] == "operator_feedback_dataset"
    assert result["count"] == 3
    assert result["action_counts"]["approved"] == 1
    assert result["outcome_counts"]["paper_success"] == 1
    assert result["validation"]["ok"] is True

def test_operator_feedback_dataset_defaults_to_pending_outcome():
    result = build_operator_feedback_dataset(MULTI_MARKET_FIXTURE)
    assert result["ok"] is True
    assert result["outcome_counts"]["pending_outcome"] == 3

def test_validate_operator_feedback_dataset_rejects_bad_type():
    with pytest.raises(ValueError, match="operator_feedback_dataset type is invalid"):
        validate_operator_feedback_dataset({"type": "bad"})

def test_paper_outcome_tracking_contract_contains_items():
    outcomes = {"BTCUSDT": "paper_success", "AAPL": "paper_neutral", "SPY": "inconclusive"}
    result = build_paper_outcome_tracking_contract(MULTI_MARKET_FIXTURE, outcome_by_symbol=outcomes)
    assert result["ok"] is True
    assert result["type"] == "paper_outcome_tracking_contract"
    assert result["count"] == 3
    assert result["items"][0]["real_world_actions_allowed"] is False
    assert result["decision"] == "outcome_tracking_paper_only_for_future_backtest"

def test_learning_memory_bundle_writes_expected_files(tmp_path):
    output_dir = tmp_path / "learning_memory_bundle"
    result = write_learning_memory_bundle(MULTI_MARKET_FIXTURE, output_dir)
    assert result["ok"] is True
    assert result["type"] == "learning_memory_bundle_written"
    assert Path(result["schema_file"]).exists()
    assert Path(result["dataset_file"]).exists()
    assert Path(result["tracking_file"]).exists()
    saved = json.loads(Path(result["dataset_file"]).read_text(encoding="utf-8"))
    assert saved["type"] == "operator_feedback_dataset"
    assert saved["validation"]["ok"] is True

def test_learning_memory_bundle_preserves_safety_flags(tmp_path):
    output_dir = tmp_path / "learning_memory_bundle_safety"
    result = write_learning_memory_bundle(MULTI_MARKET_FIXTURE, output_dir)
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_api_key_required"] is False
    assert result["wallet_private_key_required"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True
