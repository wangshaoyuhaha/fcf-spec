import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p13_operator_console_acceptance import build_operator_console_acceptance_summary
from btc_finance_platform.p13_operator_console_acceptance import write_operator_console_acceptance_summary


def test_acceptance_summary_closes_p13_scope(tmp_path):
    summary = build_operator_console_acceptance_summary(tmp_path / "index.html")

    assert summary["acceptance_status"] == "ACCEPTED_FOR_READ_ONLY_PAPER_CONSOLE"
    assert summary["p13_scope_closed"] is True
    assert summary["current_stage"] == "P13-D13-D15"


def test_acceptance_summary_keeps_paper_only_boundary(tmp_path):
    summary = build_operator_console_acceptance_summary(tmp_path / "index.html")

    assert summary["paper_only"] is True
    assert summary["local_only"] is True
    assert summary["ui_mode"] == "read_only"
    assert summary["operator_review_required"] is True


def test_acceptance_summary_blocks_real_money_execution(tmp_path):
    summary = build_operator_console_acceptance_summary(tmp_path / "index.html")

    assert summary["safe_to_execute_real_money"] is False
    assert summary["real_world_actions_allowed"] is False
    assert summary["deployment_allowed_now"] is False
    assert summary["no_real_orders"] is True
    assert summary["no_real_execution"] is True
    assert summary["no_real_money_impact"] is True


def test_write_acceptance_summary_creates_json(tmp_path):
    output = tmp_path / "index.html"
    summary_path = tmp_path / "acceptance_summary.json"

    result = write_operator_console_acceptance_summary(output, summary_path)

    assert result["ok"] is True
    assert summary_path.exists()

    data = json.loads(summary_path.read_text(encoding="utf-8"))
    assert data["type"] == "p13_operator_console_acceptance_summary"
    assert data["p13_scope_closed"] is True
    assert data["safe_to_execute_real_money"] is False
