import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.operator_evidence_console import build_operator_evidence_console_closeout_checkpoint
from btc_finance_platform.operator_evidence_console import build_operator_evidence_section_lookup
from btc_finance_platform.operator_evidence_console import build_operator_evidence_static_export_package


def test_p16_d7_operator_evidence_section_lookup_returns_release_evidence_section():
    result = build_operator_evidence_section_lookup("release_evidence")
    assert result["ok"] is True
    assert result["section"]["section_id"] == "release_evidence"
    assert result["section"]["read_only"] is True
    assert result["real_trading_enabled"] is False


def test_p16_d8_operator_evidence_static_export_package_is_local_read_only():
    package = build_operator_evidence_static_export_package()
    assert package["ok"] is True
    assert package["export_mode"] == "LOCAL_STATIC_READ_ONLY"
    assert package["safety_gate"]["status"] == "PASSED"
    assert package["deploy_enabled"] is False
    assert package["real_trading_enabled"] is False


def test_p16_d9_operator_evidence_console_closeout_checkpoint_is_safe():
    checkpoint = build_operator_evidence_console_closeout_checkpoint()
    assert checkpoint["ok"] is True
    assert checkpoint["section_count"] == 7
    assert checkpoint["safety_gate_status"] == "PASSED"
    assert checkpoint["paper_only"] is True
    assert checkpoint["deploy_enabled"] is False
    assert checkpoint["real_trading_enabled"] is False
