import json
import os
import sys
from pathlib import Path
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_operator_console import build_operator_review_queue
from btc_finance_platform.paper_operator_workflow import build_cli_to_ui_artifact_export_bridge
from btc_finance_platform.paper_operator_workflow import build_operator_review_action
from btc_finance_platform.paper_operator_workflow import build_operator_workflow_state
from btc_finance_platform.paper_operator_workflow import build_operator_workflow_summary
from btc_finance_platform.paper_operator_workflow import normalize_operator_action
from btc_finance_platform.paper_operator_workflow import validate_operator_workflow_state
from btc_finance_platform.paper_operator_workflow import write_operator_workflow_bundle

MULTI_MARKET_FIXTURE = Path(ROOT) / "fixtures" / "sample_multi_market_batch.json"

def test_normalize_operator_action_rejects_invalid_action():
    with pytest.raises(ValueError, match="operator action must be pending, approved, or rejected"):
        normalize_operator_action("live_trade")

def test_build_operator_review_action_approved_is_still_paper_only():
    queue = build_operator_review_queue(MULTI_MARKET_FIXTURE)
    result = build_operator_review_action(queue["items"][0], "approved", "looks ok")
    assert result["ok"] is True
    assert result["type"] == "operator_review_action"
    assert result["operator_action"] == "approved"
    assert result["workflow_gate"] == "paper_review_approved"
    assert result["real_world_actions_allowed"] is False
    assert result["real_order"] is False

def test_operator_workflow_state_counts_actions():
    actions = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
    result = build_operator_workflow_state(MULTI_MARKET_FIXTURE, actions)
    assert result["ok"] is True
    assert result["type"] == "operator_workflow_state"
    assert result["count"] == 3
    assert result["action_counts"]["approved"] == 1
    assert result["action_counts"]["pending"] == 1
    assert result["action_counts"]["rejected"] == 1

def test_operator_workflow_summary_detects_all_reviewed():
    actions = {"BTCUSDT": "approved", "AAPL": "approved", "SPY": "rejected"}
    result = build_operator_workflow_summary(MULTI_MARKET_FIXTURE, actions)
    assert result["ok"] is True
    assert result["type"] == "operator_workflow_summary"
    assert result["all_reviewed"] is True
    assert result["allowed_global_next_step"] == "paper_archive_only"
    assert result["real_world_actions_allowed"] is False

def test_validate_operator_workflow_state_passes():
    state = build_operator_workflow_state(MULTI_MARKET_FIXTURE)
    result = validate_operator_workflow_state(state)
    assert result["ok"] is True
    assert result["type"] == "operator_workflow_state_validation"
    assert all(result["checks"].values())

def test_validate_operator_workflow_state_rejects_bad_type():
    with pytest.raises(ValueError, match="operator_workflow_state type is invalid"):
        validate_operator_workflow_state({"type": "bad"})

def test_cli_to_ui_artifact_export_bridge_contains_console_and_workflow():
    result = build_cli_to_ui_artifact_export_bridge(MULTI_MARKET_FIXTURE)
    assert result["ok"] is True
    assert result["type"] == "cli_to_ui_artifact_export_bridge"
    assert result["bridge_version"] == "p7_d6_cli_to_ui_bridge_v1"
    assert result["workflow_validation"]["ok"] is True
    assert "operator_workflow_state.json" in result["export_targets"]

def test_operator_workflow_bundle_preserves_safety_flags(tmp_path):
    output_dir = tmp_path / "operator_workflow_bundle"
    result = write_operator_workflow_bundle(MULTI_MARKET_FIXTURE, output_dir)
    assert result["ok"] is True
    assert result["type"] == "operator_workflow_bundle_written"
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True
    assert Path(result["bridge_file"]).exists()
    saved = json.loads(Path(result["bridge_file"]).read_text(encoding="utf-8"))
    assert saved["type"] == "cli_to_ui_artifact_export_bridge"
