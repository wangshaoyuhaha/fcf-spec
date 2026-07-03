import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p13_operator_console_snapshot import build_operator_console_status_snapshot
from btc_finance_platform.p13_operator_console_snapshot import write_operator_console_status_snapshot


def test_snapshot_is_read_only_local_paper_only(tmp_path):
    result = build_operator_console_status_snapshot(tmp_path / "index.html")

    assert result["status_line"] == "READ_ONLY_LOCAL_PAPER_OPERATOR_REVIEW_REQUIRED"
    assert result["ui_mode"] == "read_only"
    assert result["local_only"] is True
    assert result["paper_only"] is True
    assert result["operator_review_required"] is True


def test_snapshot_never_enables_real_actions(tmp_path):
    result = build_operator_console_status_snapshot(tmp_path / "index.html")

    assert result["trading_buttons_enabled"] is False
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_balance"] is False
    assert result["real_position"] is False
    assert result["real_money_impact"] is False
    assert result["real_world_actions_allowed"] is False


def test_snapshot_documents_forbidden_actions(tmp_path):
    result = build_operator_console_status_snapshot(tmp_path / "index.html")

    assert "no_trading_buttons" in result["forbidden_actions"]
    assert "no_real_orders" in result["forbidden_actions"]
    assert "no_real_execution" in result["forbidden_actions"]
    assert "no_real_money_impact" in result["forbidden_actions"]


def test_snapshot_write_creates_json_file(tmp_path):
    output = tmp_path / "index.html"
    snapshot_path = tmp_path / "status_snapshot.json"

    result = write_operator_console_status_snapshot(output, snapshot_path)

    assert result["ok"] is True
    assert snapshot_path.exists()

    data = json.loads(snapshot_path.read_text(encoding="utf-8"))
    assert data["type"] == "p13_operator_console_status_snapshot"
    assert data["operator_console_ready"] is True
    assert data["trading_buttons_enabled"] is False
