import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p13_ai_learning_audit_report import build_ai_learning_audit_report
from btc_finance_platform.p13_ai_learning_audit_report import load_learning_ledger
from btc_finance_platform.p13_ai_learning_audit_report import write_ai_learning_audit_report


def test_load_learning_ledger_returns_empty_when_missing(tmp_path):
    ledger = load_learning_ledger(tmp_path / "missing.json")

    assert ledger["type"] == "p13_ai_learning_memory_ledger"
    assert ledger["event_count"] == 0
    assert ledger["events"] == []


def test_audit_report_is_operator_review_only(tmp_path):
    report = build_ai_learning_audit_report(tmp_path / "missing.json")

    assert report["audit_status"] == "READY_FOR_OPERATOR_REVIEW"
    assert report["operator_review_required"] is True
    assert report["learning_mode"] == "audit_and_proposal_only"


def test_audit_report_blocks_auto_patch_and_real_actions(tmp_path):
    report = build_ai_learning_audit_report(tmp_path / "missing.json")

    assert report["patch_policy"]["patch_proposal_allowed"] is True
    assert report["patch_policy"]["patch_auto_apply_allowed"] is False
    assert report["patch_policy"]["auto_merge_allowed"] is False
    assert report["real_world_actions_allowed"] is False
    assert report["real_execution"] is False


def test_audit_report_documents_bug_detection_limits(tmp_path):
    report = build_ai_learning_audit_report(tmp_path / "missing.json")

    assert "missing_required_fields" in report["bug_detection_scope"]
    assert "sensitive_memory_rejection" in report["bug_detection_scope"]
    assert "cannot_prove_absence_of_all_bugs" in report["bug_detection_limitations"]


def test_audit_report_rejects_invalid_ledger_type(tmp_path):
    ledger = tmp_path / "ledger.json"
    ledger.write_text(json.dumps({"type": "wrong"}), encoding="utf-8")

    with pytest.raises(ValueError, match="invalid learning ledger type"):
        build_ai_learning_audit_report(ledger)


def test_write_ai_learning_audit_report_creates_json(tmp_path):
    ledger = tmp_path / "missing.json"
    report_path = tmp_path / "ai_learning_audit_report.json"

    result = write_ai_learning_audit_report(ledger, report_path)

    assert result["ok"] is True
    assert report_path.exists()

    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert data["type"] == "p13_ai_learning_audit_report"
    assert data["patch_policy"]["patch_auto_apply_allowed"] is False
