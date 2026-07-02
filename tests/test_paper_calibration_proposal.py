import json
import os
import sys
from pathlib import Path
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_calibration_proposal import (
    build_calibration_proposal_contract,
    build_calibration_ui_contract,
    build_risk_bucket_performance_index,
    validate_calibration_ui_contract,
    write_calibration_proposal_bundle,
)

MULTI_MARKET_FIXTURE = Path(ROOT) / "fixtures" / "sample_multi_market_batch.json"
ACTIONS = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
OUTCOMES = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}


def test_risk_bucket_performance_index_builds():
    result = build_risk_bucket_performance_index(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "risk_bucket_performance_index"
    assert result["bucket_count"] >= 1
    assert result["training_status"] == "not_trained"


def test_calibration_proposal_requires_operator_review():
    result = build_calibration_proposal_contract(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "calibration_proposal_contract"
    assert result["proposal_count"] >= 1
    assert all(item["parameter_update_allowed_now"] is False for item in result["proposals"])


def test_calibration_ui_contract_validation_passes():
    result = build_calibration_ui_contract(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "calibration_ui_contract"
    assert result["validation"]["ok"] is True
    assert result["calibration_status"] == "not_calibrated"


def test_validate_calibration_ui_contract_rejects_bad_type():
    with pytest.raises(ValueError, match="calibration_ui_contract type is invalid"):
        validate_calibration_ui_contract({"type": "bad"})


def test_calibration_ui_contract_preserves_safety():
    result = build_calibration_ui_contract(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["paper_only"] is True
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True


def test_write_calibration_proposal_bundle(tmp_path):
    output_dir = tmp_path / "calibration_proposal_bundle"
    result = write_calibration_proposal_bundle(MULTI_MARKET_FIXTURE, output_dir, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert Path(result["performance_file"]).exists()
    assert Path(result["proposal_file"]).exists()
    assert Path(result["ui_file"]).exists()
    saved = json.loads(Path(result["ui_file"]).read_text(encoding="utf-8"))
    assert saved["type"] == "calibration_ui_contract"


def test_written_calibration_bundle_preserves_safety(tmp_path):
    output_dir = tmp_path / "calibration_proposal_bundle_safety"
    result = write_calibration_proposal_bundle(MULTI_MARKET_FIXTURE, output_dir, ACTIONS, OUTCOMES)
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
