import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p13_operator_console import build_operator_console_state
from btc_finance_platform.p13_operator_console import render_operator_console_html
from btc_finance_platform.p13_operator_console import write_operator_console_html

def project(extra=None):
    data = {"project_name": "BTC finance platform", "current_stage": "P13-D1-D3", "paper_only": True, "operator_review_required": True, "ui_mode": "read_only", "local_only": True}
    if extra:
        data.update(extra)
    return data

def validation(extra=None):
    data = {"all_checks_passed": True, "pytest_passed": True, "pytest_count": 433}
    if extra:
        data.update(extra)
    return data

def release(extra=None):
    data = {"release_published": True, "release_tag": "v12-paper-final-archive"}
    if extra:
        data.update(extra)
    return data

def test_operator_console_state_ready_for_read_only_paper_console():
    result = build_operator_console_state(project(), validation(), release())
    assert result["console_status"] == "ready"
    assert result["operator_console_ready"] is True
    assert result["trading_buttons_enabled"] is False

def test_operator_console_blocks_failed_validation():
    result = build_operator_console_state(project(), validation({"pytest_passed": False}), release())
    assert result["console_status"] == "blocked"
    assert "check_failed:validation_passed" in result["blocked_reasons"]

def test_operator_console_blocks_real_order_flag():
    result = build_operator_console_state(project({"real_order": True}), validation(), release())
    assert result["console_status"] == "blocked"
    assert "check_failed:no_forbidden_real_action_flags" in result["blocked_reasons"]
    assert result["real_order"] is False

def test_operator_console_html_is_read_only_and_paper_only():
    state = build_operator_console_state(project(), validation(), release())
    html = render_operator_console_html(state)
    assert "read-only" in html
    assert "paper-only" in html
    assert "No trading buttons" in html

def test_operator_console_write_html_creates_file(tmp_path):
    state = build_operator_console_state(project(), validation(), release())
    output = tmp_path / "index.html"
    result = write_operator_console_html(state, output)
    assert result["ok"] is True
    assert output.exists()
    assert "Operator Console" in output.read_text(encoding="utf-8")

def test_operator_console_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="project_state must be a dict"):
        build_operator_console_state(None, validation(), release())
    with pytest.raises(ValueError, match="state must be a dict"):
        render_operator_console_html(None)
