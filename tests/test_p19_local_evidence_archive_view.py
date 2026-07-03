import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.operator_evidence_archive_view import build_operator_evidence_archive_index
from btc_finance_platform.operator_evidence_archive_view import build_operator_evidence_archive_overview
from btc_finance_platform.operator_evidence_archive_view import resolve_operator_evidence_archive


def test_p19_d1_archive_index_lists_p14_to_p18():
    index = build_operator_evidence_archive_index()
    assert index["ok"] is True
    assert index["archive_count"] == 5
    assert index["release_tag"] == "v14-learning-engine-paper"
    assert index["deploy_enabled"] is False
    assert index["real_trading_enabled"] is False


def test_p19_d2_archive_resolver_finds_p18_navigation_archive():
    result = resolve_operator_evidence_archive("p18_navigation")
    assert result["ok"] is True
    assert result["archive"]["status"] == "COMPLETED"
    assert result["read_only"] is True
    assert result["paper_only"] is True
    assert result["real_trading_enabled"] is False


def test_p19_d3_archive_overview_is_read_only_and_safe():
    overview = build_operator_evidence_archive_overview()
    assert overview["ok"] is True
    assert overview["archive_count"] == 5
    assert overview["export_handoff_status"] == "READY_FOR_OPERATOR_REVIEW"
    assert overview["navigation_safety_gate_status"] == "PASSED"
    assert overview["operator_review_required"] is True
