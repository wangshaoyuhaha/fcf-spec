import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_model_card import (
    build_model_registry_readable_report,
    build_operator_model_approval_gate,
    build_paper_model_card,
    write_model_card_report_bundle,
)

MULTI_MARKET_FIXTURE = Path(ROOT) / "fixtures" / "sample_multi_market_batch.json"
ACTIONS = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
OUTCOMES = {"BTCUSDT": "paper_success", "AAPL": "pending_outcome", "SPY": "paper_failure"}


def test_paper_model_card_builds():
    result = build_paper_model_card(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "paper_model_card"
    assert result["training_status"] == "not_trained"
    assert result["deployment_status"] == "not_deployed"


def test_model_card_forbids_live_use():
    result = build_paper_model_card(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert "automatic live trading" in result["forbidden_use"]
    assert result["parameter_update_allowed_now"] is False
    assert result["real_world_actions_allowed"] is False


def test_operator_model_approval_gate_passes_but_blocks_deployment():
    result = build_operator_model_approval_gate(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["gate"] == "pass"
    assert result["deployment_allowed_now"] is False
    assert result["approval_status"] == "operator_review_required_before_future_model_change"


def test_model_registry_readable_report_contains_notice():
    result = build_model_registry_readable_report(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert result["type"] == "model_registry_readable_report"
    assert "# Paper Model Registry Report" in result["markdown"]
    assert "This report does not deploy a model." in result["markdown"]


def test_model_card_report_preserves_safety():
    result = build_model_registry_readable_report(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True


def test_write_model_card_report_bundle(tmp_path):
    output_dir = tmp_path / "model_card_bundle"
    result = write_model_card_report_bundle(MULTI_MARKET_FIXTURE, output_dir, ACTIONS, OUTCOMES)
    assert result["ok"] is True
    assert Path(result["card_file"]).exists()
    assert Path(result["gate_file"]).exists()
    assert Path(result["report_file"]).exists()


def test_written_model_card_bundle_preserves_safety(tmp_path):
    output_dir = tmp_path / "model_card_bundle_safety"
    result = write_model_card_report_bundle(MULTI_MARKET_FIXTURE, output_dir, ACTIONS, OUTCOMES)
    assert result["paper_only"] is True
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False

def test_model_registry_report_has_real_world_actions_allowed_field():
    result = build_model_registry_readable_report(MULTI_MARKET_FIXTURE, ACTIONS, OUTCOMES)
    assert result["real_world_actions_allowed"] is False
    assert result["deployment_allowed_now"] is False
    assert result["parameter_update_allowed_now"] is False
