import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_final_operator_acceptance_packet import REQUIRED_ACCEPTANCE_ITEMS
from btc_finance_platform.p14_final_operator_acceptance_packet import build_final_operator_acceptance_packet
from btc_finance_platform.p14_final_operator_acceptance_packet import default_operator_acceptance_items
from btc_finance_platform.p14_final_operator_acceptance_packet import normalize_acceptance_item
from btc_finance_platform.p14_final_operator_acceptance_packet import write_final_operator_acceptance_packet


def test_default_operator_acceptance_items_cover_required_keys():
    keys = {row["item_key"] for row in default_operator_acceptance_items()}

    assert set(REQUIRED_ACCEPTANCE_ITEMS) == keys


def test_final_operator_acceptance_packet_ready():
    packet = build_final_operator_acceptance_packet(
        "p13-operator-console",
        "main",
        default_operator_acceptance_items(),
        583,
    )

    assert packet["acceptance_status"] == "READY_FOR_FINAL_OPERATOR_ACCEPTANCE"
    assert packet["acceptance_policy"]["merge_to_main_allowed_now"] is False


def test_final_operator_acceptance_packet_blocks_missing_item():
    rows = [
        row for row in default_operator_acceptance_items()
        if row["item_key"] != "repo_clean"
    ]

    packet = build_final_operator_acceptance_packet("p13-operator-console", "main", rows, 583)

    assert packet["acceptance_status"] == "BLOCKED_MISSING_ACCEPTANCE_ITEM"
    assert "repo_clean" in packet["missing_items"]


def test_final_operator_acceptance_packet_blocks_unsafe_item():
    rows = default_operator_acceptance_items()
    rows[0]["merge_auto_execute_allowed"] = True

    packet = build_final_operator_acceptance_packet("p13-operator-console", "main", rows, 583)

    assert packet["acceptance_status"] == "BLOCKED_SAFETY_BOUNDARY_VIOLATION"
    assert packet["unsafe_item_count"] == 1


def test_final_operator_acceptance_packet_blocks_non_accepted_item():
    rows = default_operator_acceptance_items()
    rows[0]["status"] = "pending"

    packet = build_final_operator_acceptance_packet("p13-operator-console", "main", rows, 583)

    assert packet["acceptance_status"] == "BLOCKED_NON_ACCEPTED_ITEM"
    assert packet["non_accepted_item_count"] == 1


def test_final_operator_acceptance_packet_preserves_safety_boundary():
    packet = build_final_operator_acceptance_packet(
        "p13-operator-console",
        "main",
        default_operator_acceptance_items(),
        583,
    )

    assert packet["paper_only"] is True
    assert packet["local_only"] is True
    assert packet["operator_review_required"] is True
    assert packet["real_world_actions_allowed"] is False
    assert packet["real_execution"] is False


def test_normalize_acceptance_item_requires_item_key():
    with pytest.raises(ValueError, match="item_key is required"):
        normalize_acceptance_item({"status": "accepted"})


def test_write_final_operator_acceptance_packet_creates_json(tmp_path):
    output = tmp_path / "p14_final_operator_acceptance_packet.json"

    result = write_final_operator_acceptance_packet(
        "p13-operator-console",
        "main",
        default_operator_acceptance_items(),
        583,
        output,
    )

    assert result["ok"] is True
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["type"] == "p14_final_operator_acceptance_packet"
    assert data["acceptance_policy"]["merge_auto_execute_allowed"] is False
