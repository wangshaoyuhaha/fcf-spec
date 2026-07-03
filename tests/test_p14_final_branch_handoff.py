import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_final_branch_handoff import REQUIRED_HANDOFF_ITEMS
from btc_finance_platform.p14_final_branch_handoff import build_final_branch_handoff_checkpoint
from btc_finance_platform.p14_final_branch_handoff import default_final_branch_handoff_items
from btc_finance_platform.p14_final_branch_handoff import normalize_handoff_item
from btc_finance_platform.p14_final_branch_handoff import write_final_branch_handoff_checkpoint


def test_default_final_branch_handoff_items_cover_required_keys():
    keys = {row["item_key"] for row in default_final_branch_handoff_items()}

    assert set(REQUIRED_HANDOFF_ITEMS) == keys


def test_final_branch_handoff_ready_for_operator_review():
    checkpoint = build_final_branch_handoff_checkpoint(
        "p13-operator-console",
        "main",
        "add P14 final archive manifest",
        598,
        default_final_branch_handoff_items(),
    )

    assert checkpoint["handoff_status"] == "READY_FOR_OPERATOR_BRANCH_HANDOFF"
    assert checkpoint["handoff_policy"]["merge_to_main_allowed_now"] is False


def test_final_branch_handoff_blocks_missing_item():
    rows = [
        row for row in default_final_branch_handoff_items()
        if row["item_key"] != "p14_final_archive_manifest"
    ]

    checkpoint = build_final_branch_handoff_checkpoint(
        "p13-operator-console",
        "main",
        "add P14 final archive manifest",
        598,
        rows,
    )

    assert checkpoint["handoff_status"] == "BLOCKED_MISSING_HANDOFF_ITEM"
    assert "p14_final_archive_manifest" in checkpoint["missing_items"]


def test_final_branch_handoff_blocks_unsafe_item():
    rows = default_final_branch_handoff_items()
    rows[0]["merge_auto_execute_allowed"] = True

    checkpoint = build_final_branch_handoff_checkpoint(
        "p13-operator-console",
        "main",
        "add P14 final archive manifest",
        598,
        rows,
    )

    assert checkpoint["handoff_status"] == "BLOCKED_SAFETY_BOUNDARY_VIOLATION"
    assert checkpoint["unsafe_item_count"] == 1


def test_final_branch_handoff_blocks_non_ready_item():
    rows = default_final_branch_handoff_items()
    rows[0]["status"] = "pending"

    checkpoint = build_final_branch_handoff_checkpoint(
        "p13-operator-console",
        "main",
        "add P14 final archive manifest",
        598,
        rows,
    )

    assert checkpoint["handoff_status"] == "BLOCKED_NON_READY_ITEM"
    assert checkpoint["non_ready_item_count"] == 1


def test_final_branch_handoff_preserves_safety_boundary():
    checkpoint = build_final_branch_handoff_checkpoint(
        "p13-operator-console",
        "main",
        "add P14 final archive manifest",
        598,
        default_final_branch_handoff_items(),
    )

    assert checkpoint["paper_only"] is True
    assert checkpoint["local_only"] is True
    assert checkpoint["operator_review_required"] is True
    assert checkpoint["real_world_actions_allowed"] is False
    assert checkpoint["real_execution"] is False


def test_normalize_handoff_item_requires_item_key():
    with pytest.raises(ValueError, match="item_key is required"):
        normalize_handoff_item({"status": "ready"})


def test_write_final_branch_handoff_checkpoint_creates_json(tmp_path):
    output = tmp_path / "p14_final_branch_handoff_checkpoint.json"

    result = write_final_branch_handoff_checkpoint(
        "p13-operator-console",
        "main",
        "add P14 final archive manifest",
        598,
        default_final_branch_handoff_items(),
        output,
    )

    assert result["ok"] is True
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["type"] == "p14_final_branch_handoff_checkpoint"
    assert data["handoff_policy"]["merge_auto_execute_allowed"] is False
