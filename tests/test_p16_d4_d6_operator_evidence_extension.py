import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.operator_evidence_console import build_operator_evidence_readable_report
from btc_finance_platform.operator_evidence_console import evaluate_operator_evidence_console_safety
from btc_finance_platform.operator_evidence_console import resolve_operator_evidence_artifacts


def test_p16_d4_operator_evidence_artifact_resolver_indexes_all_sections():
    result = resolve_operator_evidence_artifacts()
    assert result["ok"] is True
    assert result["type"] == "operator_evidence_artifact_resolver"
    assert result["artifact_count"] == 7
    assert result["read_only"] is True
    assert result["real_trading_enabled"] is False


def test_p16_d5_operator_evidence_readable_report_is_safe_and_traceable():
    report = build_operator_evidence_readable_report()
    assert report["ok"] is True
    assert report["release_tag"] == "v14-learning-engine-paper"
    assert "P16 Operator Evidence Console Report" in report["title"]
    assert report["operator_review_required"] is True
    assert report["deploy_enabled"] is False


def test_p16_d6_operator_evidence_console_safety_gate_passes_paper_only_boundary():
    gate = evaluate_operator_evidence_console_safety()
    assert gate["ok"] is True
    assert gate["status"] == "PASSED"
    assert gate["paper_only"] is True
    assert gate["read_only"] is True
    assert gate["real_trading_enabled"] is False
    assert gate["deploy_enabled"] is False
