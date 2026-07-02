import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_backtest_baseline import (
    build_calibration_seed_baseline,
    build_paper_backtest_baseline,
    build_paper_backtest_input_contract,
    score_paper_outcome,
    write_paper_backtest_baseline_bundle,
)

MULTI_MARKET_FIXTURE = Path(ROOT) / "fixtures" / "sample_multi_market_batch.json"
ACTIONS = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
OUTCOMES = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}


def test_backtest_input_contract_contains_rows():
    result = build_paper_backtest_input_contract(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "paper_backtest_input_contract"
    assert result["count"] == 3
    assert result["training_status"] == "not_trained"


def test_score_paper_success_and_failure():
    success = score_paper_outcome({"symbol": "BTCUSDT", "paper_outcome_status": "paper_success"})
    failure = score_paper_outcome({"symbol": "SPY", "paper_outcome_status": "paper_failure"})
    assert success["outcome_score"] == 1.0
    assert failure["outcome_score"] == -1.0
    assert success["usable_for_calibration"] is True
    assert failure["usable_for_calibration"] is True


def test_score_pending_is_not_usable_for_calibration():
    pending = score_paper_outcome({"symbol": "AAPL", "paper_outcome_status": "pending_outcome"})
    assert pending["outcome_score"] == 0.0
    assert pending["usable_for_calibration"] is False


def test_backtest_baseline_scores_rows():
    result = build_paper_backtest_baseline(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "paper_backtest_baseline"
    assert result["count"] == 3
    assert result["usable_count"] == 2
    assert result["calibration_status"] == "not_calibrated"


def test_calibration_seed_groups_by_risk_level():
    result = build_calibration_seed_baseline(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "calibration_seed_baseline"
    assert result["training_status"] == "not_trained"
    assert isinstance(result["by_risk_level"], dict)


def test_backtest_bundle_writes_files(tmp_path):
    output_dir = tmp_path / "backtest_bundle"
    result = write_paper_backtest_baseline_bundle(MULTI_MARKET_FIXTURE, output_dir, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert Path(result["contract_file"]).exists()
    assert Path(result["backtest_file"]).exists()
    assert Path(result["seed_file"]).exists()
    saved = json.loads(Path(result["seed_file"]).read_text(encoding="utf-8"))
    assert saved["type"] == "calibration_seed_baseline"


def test_backtest_bundle_preserves_safety_flags(tmp_path):
    output_dir = tmp_path / "backtest_bundle_safety"
    result = write_paper_backtest_baseline_bundle(MULTI_MARKET_FIXTURE, output_dir, ACTIONS, OUTCOMES)
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True
