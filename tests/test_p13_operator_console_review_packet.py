import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p13_operator_console_review_packet import build_operator_review_packet
from btc_finance_platform.p13_operator_console_review_packet import write_operator_review_packet


def test_review_packet_requires_operator_review(tmp_path):
    packet = build_operator_review_packet(tmp_path / "index.html")

    assert packet["review_status"] == "WAITING_FOR_OPERATOR_REVIEW"
    assert packet["operator_action_allowed"] == "review_only"
    assert packet["operator_review_required"] is True


def test_review_packet_ai_mode_is_paper_only(tmp_path):
    packet = build_operator_review_packet(tmp_path / "index.html")

    assert packet["ai_advice_mode"] == "paper_decision_draft_only"
    assert packet["safe_to_execute_real_money"] is False
    assert packet["real_world_actions_allowed"] is False


def test_review_packet_forbids_real_market_actions(tmp_path):
    packet = build_operator_review_packet(tmp_path / "index.html")

    assert "place_order" in packet["forbidden_actions"]
    assert "execute_trade" in packet["forbidden_actions"]
    assert "connect_exchange" in packet["forbidden_actions"]
    assert "impact_real_money" in packet["forbidden_actions"]
    assert packet["trading_buttons_enabled"] is False
    assert packet["real_execution"] is False


def test_write_review_packet_creates_json(tmp_path):
    output = tmp_path / "index.html"
    packet_path = tmp_path / "operator_review_packet.json"

    result = write_operator_review_packet(output, packet_path)

    assert result["ok"] is True
    assert packet_path.exists()

    data = json.loads(packet_path.read_text(encoding="utf-8"))
    assert data["type"] == "p13_operator_review_packet"
    assert data["review_status"] == "WAITING_FOR_OPERATOR_REVIEW"
    assert data["safe_to_execute_real_money"] is False
