import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_backtest_closeout import (
    build_p9_closeout_package,
    get_p9_backtest_capabilities,
    get_p9_safety_acceptance,
    get_p9_to_p10_transition_anchor,
    write_p9_closeout_bundle,
)

MULTI_MARKET_FIXTURE = Path(ROOT) / "fixtures" / "sample_multi_market_batch.json"
ACTIONS = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
OUTCOMES = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}


def test_p9_capabilities_completed():
    result = get_p9_backtest_capabilities()
    assert result["ok"] is True
    assert result["phase"] == "P9"
    assert result["status"] == "completed"
    assert len(result["completed_scope"]) == 15
    assert "P10 model registry handoff readiness" in result["capabilities"]


def test_p9_safety_acceptance_passes():
    result = get_p9_safety_acceptance()
    assert result["ok"] is True
    assert result["type"] == "p9_safety_acceptance"
    assert all(result["checks"].values())


def test_p9_to_p10_transition_anchor_names_p10():
    result = get_p9_to_p10_transition_anchor()
    assert result["ok"] is True
    assert result["to_phase"] == "P10 model registry and strategy versioning"
    assert "paper model registry schema" in result["p10_candidate_scope"]


def test_p9_transition_forbids_live_deployment():
    result = get_p9_to_p10_transition_anchor()
    assert "automatic model deployment" in result["forbidden"]
    assert "real money impact" in result["forbidden"]


def test_build_p9_closeout_package():
    result = build_p9_closeout_package(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "p9_closeout_package"
    assert result["phase"] == "P9"
    assert result["next_phase"] == "P10 model registry and strategy versioning"
    assert result["decision"] == "P9_closed_paper_only_ready_for_P10"


def test_p9_closeout_preserves_safety_flags():
    result = build_p9_closeout_package(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True


def test_write_p9_closeout_bundle(tmp_path):
    output_dir = tmp_path / "p9_closeout_bundle"
    result = write_p9_closeout_bundle(MULTI_MARKET_FIXTURE, output_dir, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert Path(result["package_file"]).exists()
    saved = json.loads(Path(result["package_file"]).read_text(encoding="utf-8"))
    assert saved["type"] == "p9_closeout_package"
    assert saved["next_phase"] == "P10 model registry and strategy versioning"
