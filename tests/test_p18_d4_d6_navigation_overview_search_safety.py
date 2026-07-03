import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.operator_evidence_navigation import build_operator_evidence_navigation_overview
from btc_finance_platform.operator_evidence_navigation import evaluate_operator_evidence_navigation_safety
from btc_finance_platform.operator_evidence_navigation import search_operator_evidence_sections


def test_p18_d4_navigation_overview_summarizes_routes_and_release():
    overview = build_operator_evidence_navigation_overview()
    assert overview["ok"] is True
    assert overview["release_tag"] == "v14-learning-engine-paper"
    assert overview["route_count"] == 7
    assert "release_evidence" in overview["available_sections"]
    assert overview["deploy_enabled"] is False


def test_p18_d5_section_search_finds_patch_review_route():
    result = search_operator_evidence_sections("patch")
    assert result["ok"] is True
    assert result["match_count"] >= 1
    assert any(match["section_id"] == "patch_review" for match in result["matches"])
    assert result["read_only"] is True
    assert result["real_trading_enabled"] is False


def test_p18_d6_navigation_safety_gate_passes_read_only_boundary():
    gate = evaluate_operator_evidence_navigation_safety()
    assert gate["ok"] is True
    assert gate["status"] == "PASSED"
    assert gate["all_routes_read_only"] is True
    assert gate["deploy_enabled"] is False
    assert gate["real_trading_enabled"] is False
