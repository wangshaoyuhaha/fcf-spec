import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p13_ai_learning_boundary import build_ai_learning_self_audit_boundary
from btc_finance_platform.p13_ai_learning_boundary import write_ai_learning_self_audit_boundary


def test_ai_learning_boundary_allows_learning_but_not_execution():
    boundary = build_ai_learning_self_audit_boundary()

    assert boundary["learning_enabled"] is True
    assert boundary["learning_mode"] == "audit_and_proposal_only"
    assert boundary["ai_may_generate_patch_proposal"] is True
    assert boundary["ai_may_generate_tests"] is True
    assert boundary["ai_may_place_real_order"] is False
    assert boundary["ai_may_adjust_real_money"] is False


def test_ai_learning_boundary_requires_memory_and_audit():
    boundary = build_ai_learning_self_audit_boundary()

    assert boundary["memory_required"] is True
    assert boundary["self_audit_enabled"] is True
    assert boundary["bug_detection_enabled"] is True
    assert "decision_log_memory" in boundary["memory_layers"]
    assert "operator_review_memory" in boundary["memory_layers"]


def test_ai_learning_boundary_forbids_sensitive_memory_and_auto_patch():
    boundary = build_ai_learning_self_audit_boundary()

    assert boundary["patch_auto_apply_allowed"] is False
    assert boundary["auto_merge_allowed"] is False
    assert boundary["auto_release_allowed"] is False
    assert "api_keys" in boundary["forbidden_memory"]
    assert "wallet_private_keys" in boundary["forbidden_memory"]


def test_ai_learning_boundary_preserves_paper_only_safety():
    boundary = build_ai_learning_self_audit_boundary()

    assert boundary["paper_only"] is True
    assert boundary["local_only"] is True
    assert boundary["ui_mode"] == "read_only"
    assert boundary["operator_review_required"] is True
    assert boundary["real_world_actions_allowed"] is False
    assert boundary["real_execution"] is False


def test_write_ai_learning_boundary_creates_json(tmp_path):
    output = tmp_path / "ai_learning_self_audit_boundary.json"
    result = write_ai_learning_self_audit_boundary(output)

    assert result["ok"] is True
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["type"] == "p13_ai_learning_self_audit_boundary"
    assert data["patch_auto_apply_allowed"] is False
    assert data["operator_review_required"] is True
