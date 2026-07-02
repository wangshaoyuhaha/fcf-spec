import json
import os
import sys
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_governance_audit import build_governance_audit_trail
from btc_finance_platform.paper_governance_report import build_governance_markdown_report
from btc_finance_platform.paper_governance_report import build_governance_report_summary
from btc_finance_platform.paper_governance_report import build_governance_symbol_markdown_section
from btc_finance_platform.paper_governance_report import require_governance_audit_trail
from btc_finance_platform.paper_governance_report import write_governance_report_bundle


JSON_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.json"
CSV_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.csv"
SOURCES = [JSON_FIXTURE, CSV_FIXTURE]


def test_require_governance_audit_trail_rejects_bad_type():
    with pytest.raises(ValueError, match="governance_audit_trail type is invalid"):
        require_governance_audit_trail({"ok": True, "type": "bad"})


def test_build_governance_report_summary():
    result = build_governance_report_summary(SOURCES)

    assert result["ok"] is True
    assert result["type"] == "governance_report_summary"
    assert result["count"] == 6
    assert result["event_count"] == 12
    assert result["decision"] == "governance_summary_paper_only"


def test_build_governance_symbol_markdown_section_contains_fields():
    trail = build_governance_audit_trail(SOURCES)
    governance_report = trail["governance_report"]
    section = build_governance_symbol_markdown_section(
        governance_report["governor_decisions"][0],
        governance_report["policy_gates"][0],
    )

    assert "### BTCUSDT" in section
    assert "Governor gate:" in section
    assert "Risk level:" in section
    assert "Regime:" in section
    assert "Policy gate:" in section


def test_build_governance_markdown_report_contains_summary_constraints_and_notice():
    result = build_governance_markdown_report(SOURCES)

    assert result["ok"] is True
    assert result["type"] == "governance_markdown_report"
    assert "# Paper Governance Report" in result["markdown"]
    assert "## Policy Constraints" in result["markdown"]
    assert "## Symbol Governance Items" in result["markdown"]
    assert "Operator approval still does not permit real-world trading actions." in result["markdown"]


def test_governance_markdown_report_preserves_safety_flags():
    result = build_governance_markdown_report(SOURCES)

    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_api_key_required"] is False
    assert result["wallet_private_key_required"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_balance"] is False
    assert result["real_position"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True


def test_write_governance_report_bundle(tmp_path):
    output_dir = tmp_path / "governance_bundle"
    result = write_governance_report_bundle(SOURCES, output_dir)

    assert result["ok"] is True
    assert result["type"] == "governance_report_bundle_written"
    assert Path(result["markdown_file"]).exists()
    assert Path(result["json_file"]).exists()

    saved = json.loads(Path(result["json_file"]).read_text(encoding="utf-8"))
    assert saved["type"] == "governance_markdown_report"
    assert saved["ok"] is True


def test_governance_report_summary_operator_gate_pending():
    result = build_governance_report_summary(SOURCES, operator_status="pending")

    assert result["operator_gate"]["gate"] == "operator_review_pending"
    assert result["operator_gate"]["real_world_actions_allowed"] is False


def test_governance_report_bundle_with_approved_status_still_no_real_world_actions(tmp_path):
    output_dir = tmp_path / "approved_bundle"
    result = write_governance_report_bundle(SOURCES, output_dir, operator_status="approved")

    operator_gate = result["report"]["summary"]["operator_gate"]
    assert result["ok"] is True
    assert operator_gate["operator_status"] == "approved"
    assert operator_gate["real_world_actions_allowed"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
