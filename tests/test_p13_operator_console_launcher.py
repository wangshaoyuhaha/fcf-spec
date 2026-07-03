import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p13_operator_console_launcher import build_operator_console_launch_plan
from btc_finance_platform.p13_operator_console_launcher import default_operator_console_inputs


def test_default_operator_console_inputs_are_paper_only():
    inputs = default_operator_console_inputs()
    assert inputs["project_state"]["paper_only"] is True
    assert inputs["project_state"]["trading_buttons_enabled"] is False
    assert inputs["validation_summary"]["all_checks_passed"] is True


def test_launcher_builds_local_read_only_console(tmp_path):
    output = tmp_path / "operator_console.html"
    result = build_operator_console_launch_plan(output)
    assert result["launch_status"] == "ready"
    assert result["operator_console_ready"] is True
    assert result["local_only"] is True
    assert result["ui_mode"] == "read_only"
    assert output.exists()


def test_launcher_never_enables_real_actions(tmp_path):
    result = build_operator_console_launch_plan(tmp_path / "index.html")
    assert result["trading_buttons_enabled"] is False
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False


def test_launcher_exposes_file_url(tmp_path):
    result = build_operator_console_launch_plan(tmp_path / "index.html")
    assert result["file_url"].startswith("file:///")
    assert result["output_path"].endswith("index.html")
