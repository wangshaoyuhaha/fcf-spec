import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.operator_evidence_archive_view import build_operator_evidence_archive_timeline
from btc_finance_platform.operator_evidence_archive_view import evaluate_operator_evidence_archive_safety
from btc_finance_platform.operator_evidence_archive_view import search_operator_evidence_archives


def test_p19_d4_archive_timeline_lists_all_archive_items_in_order():
    timeline = build_operator_evidence_archive_timeline()
    assert timeline["ok"] is True
    assert timeline["timeline_count"] == 5
    assert timeline["timeline"][0]["archive_id"] == "p14_release"
    assert timeline["read_only"] is True
    assert timeline["deploy_enabled"] is False


def test_p19_d5_archive_search_finds_p17_export_archive():
    result = search_operator_evidence_archives("export")
    assert result["ok"] is True
    assert result["match_count"] >= 1
    assert any(match["archive_id"] == "p17_export_files" for match in result["matches"])
    assert result["local_only"] is True
    assert result["real_trading_enabled"] is False


def test_p19_d6_archive_safety_gate_passes_no_deploy_boundary():
    gate = evaluate_operator_evidence_archive_safety()
    assert gate["ok"] is True
    assert gate["status"] == "PASSED"
    assert gate["archive_count"] == 5
    assert gate["all_completed_or_released"] is True
    assert gate["deploy_enabled"] is False
    assert gate["real_trading_enabled"] is False
