import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_patch_proposal_sandbox import build_patch_proposal
from btc_finance_platform.p14_patch_proposal_sandbox import validate_patch_proposal_gate
from btc_finance_platform.p14_patch_proposal_sandbox import write_patch_proposal


def safe_proposal():
    return build_patch_proposal(
        proposal_id="patch_001",
        title="safe paper-only patch proposal",
        rationale="improve local paper audit report",
        target_files=["src/btc_finance_platform/paper_audit.py"],
        test_plan=["python scripts/run_all_checks.py"],
    )


def test_patch_proposal_is_proposal_only():
    proposal = safe_proposal()

    assert proposal["ai_patch_design_allowed"] is True
    assert proposal["patch_auto_apply_allowed"] is False
    assert proposal["auto_commit_allowed"] is False
    assert proposal["auto_merge_allowed"] is False
    assert proposal["operator_review_required"] is True


def test_patch_proposal_gate_passes_safe_proposal():
    proposal = safe_proposal()
    gate = validate_patch_proposal_gate(proposal)

    assert gate["gate_status"] == "passed"
    assert gate["scenario_review_required"] is True
    assert gate["patch_auto_apply_allowed"] is False


def test_patch_proposal_rejects_forbidden_targets():
    with pytest.raises(ValueError, match="forbidden patch target detected"):
        build_patch_proposal(
            proposal_id="bad",
            title="bad",
            rationale="bad",
            target_files=["src/exchange_api.py"],
            test_plan=["python -m pytest -q"],
        )


def test_patch_proposal_gate_blocks_modified_auto_apply():
    proposal = safe_proposal()
    proposal["patch_auto_apply_allowed"] = True

    gate = validate_patch_proposal_gate(proposal)

    assert gate["gate_status"] == "blocked"
    assert "patch_auto_apply_allowed" in gate["failed_fields"]


def test_patch_proposal_preserves_paper_only_boundary():
    proposal = safe_proposal()

    assert proposal["paper_only"] is True
    assert proposal["local_only"] is True
    assert proposal["real_world_actions_allowed"] is False
    assert proposal["real_order"] is False
    assert proposal["real_execution"] is False


def test_write_patch_proposal_creates_json(tmp_path):
    output = tmp_path / "patch_proposal_record.json"
    proposal = safe_proposal()

    result = write_patch_proposal(proposal, output)

    assert result["ok"] is True
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["type"] == "p14_patch_proposal_record"
    assert data["gate"]["gate_status"] == "passed"
    assert data["patch_auto_apply_allowed"] is False
