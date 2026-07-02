import json
import os
import sys
from pathlib import Path
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_model_registry import (
    build_calibration_proposal_version_record,
    build_model_registry_baseline,
    build_paper_model_registry_schema,
    build_strategy_version_record,
    validate_model_registry_baseline,
    write_model_registry_baseline_bundle,
)

MULTI_MARKET_FIXTURE = Path(ROOT) / "fixtures" / "sample_multi_market_batch.json"
ACTIONS = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
OUTCOMES = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}


def test_model_registry_schema_contains_required_fields():
    result = build_paper_model_registry_schema()
    assert result["ok"] is True
    assert result["type"] == "paper_model_registry_schema"
    assert "model_version_id" in result["required_fields"]
    assert "operator_approval_status" in result["required_fields"]


def test_strategy_version_record_is_not_deployed():
    result = build_strategy_version_record(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "strategy_version_record"
    assert result["training_status"] == "not_trained"
    assert result["deployment_status"] == "not_deployed"
    assert result["parameter_update_allowed_now"] is False


def test_calibration_proposal_version_record_blocks_updates():
    result = build_calibration_proposal_version_record(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "calibration_proposal_version_record"
    assert result["parameter_update_allowed_now"] is False
    assert result["real_world_actions_allowed"] is False


def test_model_registry_baseline_validates():
    result = build_model_registry_baseline(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "model_registry_baseline"
    assert result["validation"]["ok"] is True
    assert result["deployment_status"] == "not_deployed"


def test_validate_model_registry_baseline_rejects_bad_type():
    with pytest.raises(ValueError, match="model_registry_baseline type is invalid"):
        validate_model_registry_baseline({"type": "bad"})


def test_model_registry_baseline_preserves_safety_flags():
    result = build_model_registry_baseline(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True


def test_write_model_registry_baseline_bundle(tmp_path):
    output_dir = tmp_path / "model_registry_bundle"
    result = write_model_registry_baseline_bundle(MULTI_MARKET_FIXTURE, output_dir, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert Path(result["schema_file"]).exists()
    assert Path(result["strategy_file"]).exists()
    assert Path(result["calibration_file"]).exists()
    assert Path(result["registry_file"]).exists()
    saved = json.loads(Path(result["registry_file"]).read_text(encoding="utf-8"))
    assert saved["type"] == "model_registry_baseline"
    assert saved["validation"]["ok"] is True
