import json
import os
import sys
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_contract import build_governance_decision_index
from btc_finance_platform.paper_governance_contract import build_governance_ui_card
from btc_finance_platform.paper_governance_contract import build_governance_ui_contract
from btc_finance_platform.paper_governance_contract import require_governance_markdown_report
from btc_finance_platform.paper_governance_contract import validate_governance_ui_contract
from btc_finance_platform.paper_governance_contract import write_governance_contract_bundle
from btc_finance_platform.paper_governance_report import build_governance_markdown_report


JSON_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.json"
CSV_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.csv"
SOURCES = [JSON_FIXTURE, CSV_FIXTURE]


def test_require_governance_markdown_report_rejects_bad_type():
    with pytest.raises(ValueError, match="governance_markdown_report type is invalid"):
        require_governance_markdown_report({"ok": True, "type": "bad"})


def test_build_governance_ui_card_contains_core_fields():
    report = build_governance_markdown_report(SOURCES)
    governance_report = report["audit_trail"]["governance_report"]
    card = build_governance_ui_card(
        governance_report["governor_decisions"][0],
        governance_report["policy_gates"][0],
    )

    assert card["ok"] is True
    assert card["type"] == "governance_ui_card"
    assert card["symbol"] == "BTCUSDT"
    assert "risk_level" in card
    assert "regime" in card
    assert card["decision"] == "ui_card_paper_only_no_real_trade"


def test_build_governance_ui_contract_has_cards_and_validation():
    result = build_governance_ui_contract(SOURCES)

    assert result["ok"] is True
    assert result["type"] == "governance_ui_contract"
    assert result["contract_version"] == "p5_d10_governance_ui_contract_v1"
    assert result["count"] == 6
    assert len(result["cards"]) == 6
    assert result["validation"]["ok"] is True


def test_governance_ui_contract_preserves_safety_flags():
    result = build_governance_ui_contract(SOURCES)

    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_api_key_required"] is False
    assert result["wallet_private_key_required"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_balance"] is False
    assert result["real_position"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True


def test_validate_governance_ui_contract_rejects_bad_type():
    with pytest.raises(ValueError, match="governance_ui_contract type is invalid"):
        validate_governance_ui_contract({"type": "bad"})


def test_build_governance_decision_index():
    result = build_governance_decision_index(SOURCES)

    assert result["ok"] is True
    assert result["type"] == "governance_decision_index"
    assert result["count"] == 6
    assert "BTCUSDT" in result["by_symbol"]
    assert len(result["review_queue"]) == 6
    assert result["decision"] == "decision_index_paper_only"


def test_write_governance_contract_bundle(tmp_path):
    output_dir = tmp_path / "contract_bundle"
    result = write_governance_contract_bundle(SOURCES, output_dir)

    assert result["ok"] is True
    assert result["type"] == "governance_contract_bundle_written"
    assert Path(result["contract_file"]).exists()
    assert Path(result["index_file"]).exists()
    assert Path(result["markdown_file"]).exists()

    saved = json.loads(Path(result["contract_file"]).read_text(encoding="utf-8"))
    assert saved["type"] == "governance_ui_contract"
    assert saved["validation"]["ok"] is True


def test_approved_operator_status_still_blocks_real_world_actions(tmp_path):
    output_dir = tmp_path / "approved_contract_bundle"
    result = write_governance_contract_bundle(SOURCES, output_dir, operator_status="approved")

    contract = result["contract"]
    assert contract["operator_status"] == "approved"
    assert contract["real_order"] is False
    assert contract["real_execution"] is False
    assert contract["real_money_impact"] is False
    assert contract["operator_review_required"] is True
