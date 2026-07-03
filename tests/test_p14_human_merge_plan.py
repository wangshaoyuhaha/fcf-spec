import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_human_merge_plan import REQUIRED_PLAN_ITEMS
from btc_finance_platform.p14_human_merge_plan import build_human_merge_plan_packet
from btc_finance_platform.p14_human_merge_plan import default_human_merge_plan_items
from btc_finance_platform.p14_human_merge_plan import default_manual_merge_commands
from btc_finance_platform.p14_human_merge_plan import normalize_merge_plan_item
from btc_finance_platform.p14_human_merge_plan import write_human_merge_plan_packet


def test_default_human_merge_plan_items_cover_required_keys():
    keys = {row["item_key"] for row in default_human_merge_plan_items()}

    assert set(REQUIRED_PLAN_ITEMS) == keys


def test_manual_merge_commands_are_documented_not_executed():
    commands = default_manual_merge_commands("p13-operator-console", "main")

    assert "git merge --no-ff p13-operator-console" in commands
    assert "python scripts/run_all_checks.py" in commands


def test_human_merge_plan_ready_for_review_only():
    packet = build_human_merge_plan_packet(
        "p13-operator-console",
        "main",
        606,
        default_human_merge_plan_items(),
    )

    assert packet["plan_status"] == "READY_FOR_HUMAN_MERGE_REVIEW"
    assert packet["merge_plan_policy"]["auto_execute_allowed"] is False
    assert packet["merge_plan_policy"]["auto_merge_allowed"] is False


def test_human_merge_plan_blocks_missing_item():
    rows = [
        row for row in default_human_merge_plan_items()
        if row["item_key"] != "repo_clean"
    ]

    packet = build_human_merge_plan_packet("p13-operator-console", "main", 606, rows)

    assert packet["plan_status"] == "BLOCKED_MISSING_PLAN_ITEM"
    assert "repo_clean" in packet["missing_items"]


def test_human_merge_plan_blocks_unsafe_item():
    rows = default_human_merge_plan_items()
    rows[0]["auto_merge_allowed"] = True

    packet = build_human_merge_plan_packet("p13-operator-console", "main", 606, rows)

    assert packet["plan_status"] == "BLOCKED_SAFETY_BOUNDARY_VIOLATION"
    assert packet["unsafe_item_count"] == 1


def test_human_merge_plan_preserves_safety_boundary():
    packet = build_human_merge_plan_packet(
        "p13-operator-console",
        "main",
        606,
        default_human_merge_plan_items(),
    )

    assert packet["paper_only"] is True
    assert packet["local_only"] is True
    assert packet["operator_review_required"] is True
    assert packet["real_world_actions_allowed"] is False
    assert packet["real_execution"] is False


def test_human_merge_plan_rejects_same_branch():
    with pytest.raises(ValueError, match="source_branch and target_branch must differ"):
        build_human_merge_plan_packet("main", "main", 606, default_human_merge_plan_items())


def test_write_human_merge_plan_packet_creates_json(tmp_path):
    output = tmp_path / "p14_human_merge_plan_packet.json"

    result = write_human_merge_plan_packet(
        "p13-operator-console",
        "main",
        606,
        default_human_merge_plan_items(),
        output,
    )

    assert result["ok"] is True
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["type"] == "p14_human_merge_plan_packet"
    assert data["merge_plan_policy"]["auto_merge_allowed"] is False
