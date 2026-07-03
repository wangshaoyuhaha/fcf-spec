import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_final_completion_receipt import REQUIRED_COMPLETION_ITEMS
from btc_finance_platform.p14_final_completion_receipt import build_final_completion_receipt
from btc_finance_platform.p14_final_completion_receipt import default_final_completion_items
from btc_finance_platform.p14_final_completion_receipt import normalize_completion_item
from btc_finance_platform.p14_final_completion_receipt import write_final_completion_receipt


def test_default_final_completion_items_cover_required_keys():
    keys = {row["item_key"] for row in default_final_completion_items()}

    assert set(REQUIRED_COMPLETION_ITEMS) == keys


def test_final_completion_receipt_marks_p14_complete():
    receipt = build_final_completion_receipt(
        "p13-operator-console",
        622,
        default_final_completion_items(),
    )

    assert receipt["completion_status"] == "P14_COMPLETE_READY_FOR_HUMAN_CONTROLLED_NEXT_STEP"
    assert receipt["completion_policy"]["merge_to_main_allowed_now"] is False
    assert receipt["completion_policy"]["release_allowed_now"] is False


def test_final_completion_receipt_blocks_missing_item():
    rows = [
        row for row in default_final_completion_items()
        if row["item_key"] != "p14_human_release_plan"
    ]

    receipt = build_final_completion_receipt("p13-operator-console", 622, rows)

    assert receipt["completion_status"] == "BLOCKED_MISSING_COMPLETION_ITEM"
    assert "p14_human_release_plan" in receipt["missing_items"]


def test_final_completion_receipt_blocks_unsafe_item():
    rows = default_final_completion_items()
    rows[0]["auto_release_allowed"] = True

    receipt = build_final_completion_receipt("p13-operator-console", 622, rows)

    assert receipt["completion_status"] == "BLOCKED_SAFETY_BOUNDARY_VIOLATION"
    assert receipt["unsafe_item_count"] == 1


def test_final_completion_receipt_blocks_non_complete_item():
    rows = default_final_completion_items()
    rows[0]["status"] = "pending"

    receipt = build_final_completion_receipt("p13-operator-console", 622, rows)

    assert receipt["completion_status"] == "BLOCKED_NON_COMPLETE_ITEM"
    assert receipt["non_complete_item_count"] == 1


def test_final_completion_receipt_preserves_safety_boundary():
    receipt = build_final_completion_receipt(
        "p13-operator-console",
        622,
        default_final_completion_items(),
    )

    assert receipt["paper_only"] is True
    assert receipt["local_only"] is True
    assert receipt["operator_review_required"] is True
    assert receipt["real_world_actions_allowed"] is False
    assert receipt["real_execution"] is False


def test_normalize_completion_item_requires_item_key():
    with pytest.raises(ValueError, match="item_key is required"):
        normalize_completion_item({"status": "complete"})


def test_write_final_completion_receipt_creates_json(tmp_path):
    output = tmp_path / "p14_final_completion_receipt.json"

    result = write_final_completion_receipt(
        "p13-operator-console",
        622,
        default_final_completion_items(),
        output,
    )

    assert result["ok"] is True
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["type"] == "p14_final_completion_receipt"
    assert data["completion_policy"]["auto_release_allowed"] is False
