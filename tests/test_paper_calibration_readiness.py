import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_calibration_readiness import (
    build_backtest_ui_readiness_gate,
    build_calibration_acceptance_gate,
    build_p9_readiness_bundle,
    write_p9_readiness_bundle,
)

MULTI_MARKET_FIXTURE = Path(ROOT) / "fixtures" / "sample_multi_market_batch.json"
ACTIONS = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
OUTCOMES = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}


def test_calibration_acceptance_gate_passes():
    result = build_calibration_acceptance_gate(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["gate"] == "pass"
    assert result["training_status"] == "not_trained"
    assert result["calibration_status"] == "not_calibrated"


def test_calibration_acceptance_blocks_parameter_updates():
    result = build_calibration_acceptance_gate(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["checks"]["all_parameter_updates_blocked"] is True
    assert result["checks"]["all_real_world_actions_blocked"] is True


def test_backtest_ui_readiness_gate_passes():
    result = build_backtest_ui_readiness_gate(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["gate"] == "pass"
    assert "risk_bucket_performance" in result["view_ids"]
    assert "calibration_proposals" in result["view_ids"]


def test_p9_readiness_bundle_accepts_for_future_closeout():
    result = build_p9_readiness_bundle(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "p9_readiness_bundle"
    assert result["accepted_for"] == "future_p9_closeout_and_p10_model_registry_handoff"
    assert result["parameter_update_allowed_now"] is False


def test_p9_readiness_bundle_preserves_safety():
    result = build_p9_readiness_bundle(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True


def test_write_p9_readiness_bundle(tmp_path):
    output_dir = tmp_path / "p9_readiness_bundle"
    result = write_p9_readiness_bundle(MULTI_MARKET_FIXTURE, output_dir, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert Path(result["acceptance_file"]).exists()
    assert Path(result["ui_file"]).exists()
    assert Path(result["bundle_file"]).exists()
    saved = json.loads(Path(result["bundle_file"]).read_text(encoding="utf-8"))
    assert saved["type"] == "p9_readiness_bundle"


def test_written_p9_readiness_bundle_preserves_safety(tmp_path):
    output_dir = tmp_path / "p9_readiness_bundle_safety"
    result = write_p9_readiness_bundle(MULTI_MARKET_FIXTURE, output_dir, ACTIONS, OUTCOMES)
    assert result["paper_only"] is True
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
