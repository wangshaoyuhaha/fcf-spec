import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_human_release_plan import REQUIRED_RELEASE_PLAN_ITEMS
from btc_finance_platform.p14_human_release_plan import build_human_release_plan_packet
from btc_finance_platform.p14_human_release_plan import default_human_release_plan_items
from btc_finance_platform.p14_human_release_plan import default_manual_release_commands
from btc_finance_platform.p14_human_release_plan import normalize_release_plan_item
from btc_finance_platform.p14_human_release_plan import write_human_release_plan_packet


def test_default_human_release_plan_items_cover_required_keys():
    keys = {row["item_key"] for row in default_human_release_plan_items()}

    assert set(REQUIRED_RELEASE_PLAN_ITEMS) == keys


def test_manual_release_commands_are_documented_not_executed():
    commands = default_manual_release_commands("v14-learning-engine-paper")

    assert "git tag -a v14-learning-engine-paper -m \"P14 learning engine paper release\"" in commands
    assert "create GitHub release manually after operator review" in commands


def test_human_release_plan_ready_for_review_only():
    packet = build_human_release_plan_packet(
        "main",
        "v14-learning-engine-paper",
        614,
        default_human_release_plan_items(),
    )

    assert packet["plan_status"] == "READY_FOR_HUMAN_RELEASE_REVIEW"
    assert packet["release_plan_policy"]["auto_tag_allowed"] is False
    assert packet["release_plan_policy"]["auto_release_allowed"] is False


def test_human_release_plan_blocks_missing_item():
    rows = [
        row for row in default_human_release_plan_items()
        if row["item_key"] != "repo_clean"
    ]

    packet = build_human_release_plan_packet("main", "v14-learning-engine-paper", 614, rows)

    assert packet["plan_status"] == "BLOCKED_MISSING_RELEASE_PLAN_ITEM"
    assert "repo_clean" in packet["missing_items"]


def test_human_release_plan_blocks_unsafe_item():
    rows = default_human_release_plan_items()
    rows[0]["auto_release_allowed"] = True

    packet = build_human_release_plan_packet("main", "v14-learning-engine-paper", 614, rows)

    assert packet["plan_status"] == "BLOCKED_SAFETY_BOUNDARY_VIOLATION"
    assert packet["unsafe_item_count"] == 1


def test_human_release_plan_preserves_safety_boundary():
    packet = build_human_release_plan_packet(
        "main",
        "v14-learning-engine-paper",
        614,
        default_human_release_plan_items(),
    )

    assert packet["paper_only"] is True
    assert packet["local_only"] is True
    assert packet["operator_review_required"] is True
    assert packet["real_world_actions_allowed"] is False
    assert packet["real_execution"] is False


def test_human_release_plan_rejects_missing_tag():
    with pytest.raises(ValueError, match="tag_name is required"):
        build_human_release_plan_packet("main", "", 614, default_human_release_plan_items())


def test_write_human_release_plan_packet_creates_json(tmp_path):
    output = tmp_path / "p14_human_release_plan_packet.json"

    result = write_human_release_plan_packet(
        "main",
        "v14-learning-engine-paper",
        614,
        default_human_release_plan_items(),
        output,
    )

    assert result["ok"] is True
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["type"] == "p14_human_release_plan_packet"
    assert data["release_plan_policy"]["auto_release_allowed"] is False
