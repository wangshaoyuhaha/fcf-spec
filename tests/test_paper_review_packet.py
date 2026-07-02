import json
import os
import sys
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_analysis_logic import draft_paper_signal
from btc_finance_platform.paper_analysis_pipeline import build_paper_analysis_pipeline_report
from btc_finance_platform.paper_review_packet import build_operator_review_checklist
from btc_finance_platform.paper_review_packet import build_paper_analysis_review_packet
from btc_finance_platform.paper_review_packet import build_symbol_review_item
from btc_finance_platform.paper_review_packet import write_paper_analysis_review_packet


JSON_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.json"
CSV_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.csv"
SOURCES = [JSON_FIXTURE, CSV_FIXTURE]


def test_build_symbol_review_item_from_analysis_item():
    analysis = draft_paper_signal("BTCUSDT", 65000, 64000)
    result = build_symbol_review_item(analysis)

    assert result["ok"] is True
    assert result["type"] == "symbol_operator_review_item"
    assert result["symbol"] == "BTCUSDT"
    assert result["operator_action"] == "review_paper_signal_only"
    assert result["decision"] == "no_real_trade_review_only"


def test_build_operator_review_checklist_blocks_real_actions():
    report = build_paper_analysis_pipeline_report(SOURCES)
    result = build_operator_review_checklist(report)

    assert result["ok"] is True
    assert result["type"] == "operator_review_checklist"
    assert "real_order" in result["blocked_actions"]
    assert "automatic_live_trading" in result["blocked_actions"]
    assert result["allowed_action"] == "paper_review_only"


def test_build_paper_analysis_review_packet_contains_items_and_checklist():
    result = build_paper_analysis_review_packet(SOURCES)

    assert result["ok"] is True
    assert result["type"] == "paper_analysis_review_packet"
    assert result["count"] == 6
    assert len(result["review_items"]) == 6
    assert result["checklist"]["ok"] is True
    assert result["decision"] == "operator_review_packet_only_no_real_trade"


def test_review_packet_preserves_safety_flags():
    result = build_paper_analysis_review_packet(SOURCES)

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


def test_review_packet_has_priority_counts():
    result = build_paper_analysis_review_packet(SOURCES)

    assert isinstance(result["priority_counts"], dict)
    assert sum(result["priority_counts"].values()) == result["count"]


def test_write_paper_analysis_review_packet(tmp_path):
    output = tmp_path / "review" / "paper_analysis_review_packet.json"
    result = write_paper_analysis_review_packet(SOURCES, output)

    assert result["ok"] is True
    assert result["type"] == "paper_analysis_review_packet_written"
    assert output.exists()

    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["type"] == "paper_analysis_review_packet"
    assert saved["ok"] is True


def test_operator_review_checklist_rejects_bad_report():
    with pytest.raises(ValueError, match="pipeline_report type is invalid"):
        build_operator_review_checklist({"ok": True, "type": "bad"})
