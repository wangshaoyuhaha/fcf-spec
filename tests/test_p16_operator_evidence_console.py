import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.operator_evidence_console import build_operator_evidence_console_manifest
from btc_finance_platform.operator_evidence_console import summarize_operator_evidence_console


def test_p16_d1_operator_evidence_console_manifest_contains_release_anchor():
    manifest = build_operator_evidence_console_manifest()
    assert manifest["type"] == "operator_evidence_console_manifest"
    assert manifest["release_tag"] == "v14-learning-engine-paper"
    assert manifest["release_commit"] == "5188158"
    assert manifest["section_count"] == 7


def test_p16_d2_operator_evidence_console_sections_are_read_only():
    manifest = build_operator_evidence_console_manifest()
    assert all(section["read_only"] is True for section in manifest["sections"])
    assert "trade" in manifest["forbidden_actions"]
    assert "deploy" in manifest["forbidden_actions"]
    assert "enter_api_key" in manifest["forbidden_actions"]


def test_p16_d3_operator_evidence_console_summary_blocks_deploy_and_real_trading():
    summary = summarize_operator_evidence_console()
    assert summary["ok"] is True
    assert summary["paper_only"] is True
    assert summary["read_only"] is True
    assert summary["real_trading_enabled"] is False
    assert summary["deploy_enabled"] is False
    assert summary["operator_review_required"] is True
