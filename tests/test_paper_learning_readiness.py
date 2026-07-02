import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_learning_readiness import build_calibration_readiness_gate
from btc_finance_platform.paper_learning_readiness import build_learning_dataset_quality_gate
from btc_finance_platform.paper_learning_readiness import build_learning_readiness_bundle
from btc_finance_platform.paper_learning_readiness import build_learning_readiness_summary
from btc_finance_platform.paper_learning_readiness import write_learning_readiness_bundle

MULTI_MARKET_FIXTURE = Path(ROOT) / "fixtures" / "sample_multi_market_batch.json"
ACTIONS = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
OUTCOMES = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}

def test_learning_dataset_quality_gate_passes():
    result = build_learning_dataset_quality_gate(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["gate"] == "pass"
    assert result["count"] == 3
    assert all(result["checks"].values())

def test_calibration_readiness_gate_passes_without_training():
    result = build_calibration_readiness_gate(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["gate"] == "pass"
    assert result["training_status"] == "not_trained_not_calibrated_yet"
    assert result["next_phase"] == "P9 backtest and calibration"

def test_learning_readiness_summary_accepts_for_p9():
    result = build_learning_readiness_summary(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["quality_gate"] == "pass"
    assert result["calibration_gate"] == "pass"
    assert result["accepted_for"] == "future_p9_backtest_and_calibration_handoff"

def test_learning_readiness_bundle_contains_gates():
    result = build_learning_readiness_bundle(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "learning_readiness_bundle"
    assert result["quality_gate"]["gate"] == "pass"
    assert result["calibration_gate"]["gate"] == "pass"
    assert result["manifest"]["validation"]["ok"] is True

def test_learning_readiness_bundle_preserves_safety():
    result = build_learning_readiness_bundle(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True

def test_write_learning_readiness_bundle(tmp_path):
    output_dir = tmp_path / "learning_readiness_bundle"
    result = write_learning_readiness_bundle(MULTI_MARKET_FIXTURE, output_dir, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert Path(result["bundle_file"]).exists()
    saved = json.loads(Path(result["bundle_file"]).read_text(encoding="utf-8"))
    assert saved["type"] == "learning_readiness_bundle"
    assert saved["training_status"] == "not_trained_not_calibrated_yet"

def test_written_bundle_preserves_safety(tmp_path):
    output_dir = tmp_path / "learning_readiness_bundle_safety"
    result = write_learning_readiness_bundle(MULTI_MARKET_FIXTURE, output_dir, ACTIONS, OUTCOMES)
    assert result["paper_only"] is True
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
