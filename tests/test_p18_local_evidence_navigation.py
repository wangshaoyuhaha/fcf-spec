import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.operator_evidence_navigation import build_operator_evidence_breadcrumb
from btc_finance_platform.operator_evidence_navigation import build_operator_evidence_navigation_index
from btc_finance_platform.operator_evidence_navigation import resolve_operator_evidence_route


def test_p18_d1_navigation_index_lists_read_only_routes():
    index = build_operator_evidence_navigation_index()
    assert index["ok"] is True
    assert index["root_route"] == "/evidence"
    assert index["route_count"] == 7
    assert all(route["read_only"] is True for route in index["routes"])
    assert index["deploy_enabled"] is False
    assert index["real_trading_enabled"] is False


def test_p18_d2_route_resolver_resolves_release_evidence_section():
    result = resolve_operator_evidence_route("/evidence/release_evidence")
    assert result["ok"] is True
    assert result["view"] == "section"
    assert result["section_id"] == "release_evidence"
    assert result["section"]["read_only"] is True
    assert result["deploy_enabled"] is False


def test_p18_d3_breadcrumb_contract_is_read_only_and_local():
    breadcrumb = build_operator_evidence_breadcrumb("release_evidence")
    assert breadcrumb["ok"] is True
    assert breadcrumb["crumb_count"] == 2
    assert breadcrumb["paper_only"] is True
    assert breadcrumb["local_only"] is True
    assert breadcrumb["real_trading_enabled"] is False
