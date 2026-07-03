import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_merge_readiness_bridge import build_merge_readiness_bridge
from btc_finance_platform.p14_merge_readiness_bridge import default_merge_readiness_items
from btc_finance_platform.p14_merge_readiness_bridge import normalize_readiness_item
from btc_finance_platform.p14_merge_readiness_bridge import write_merge_readiness_bridge


def test_merge_readiness_bridge_ready_for_operator_review_only():
    report = build_merge_readiness_bridge(
        "p13-operator-console",
        "main",
        default_merge_readiness_items(),
    )

    assert report["readiness_status"] == "READY_FOR_OPERATOR_MERGE_REVIEW"
    assert report["merge_policy"]["merge_to_main_allowed_now"] is False
    assert report["merge_policy"]["release_allowed_now"] is False


def test_merge_readiness_bridge_blocks_missing_closeout():
    rows = [
        row for row in default_merge_readiness_items()
        if row["item_key"] != "p14_learning_engine_closeout"
    ]

    report = build_merge_readiness_bridge("p13-operator-console", "main", rows)

    assert report["readiness_status"] == "BLOCKED_MISSING_CLOSEOUT"
    assert "p14_learning_engine_closeout" in report["missing_closeouts"]


def test_merge_readiness_bridge_blocks_unsafe_item():
    rows = default_merge_readiness_items()
    rows[0]["merge_auto_apply_allowed"] = True

    report = build_merge_readiness_bridge("p13-operator-console", "main", rows)

    assert report["readiness_status"] == "BLOCKED_SAFETY_BOUNDARY_VIOLATION"
    assert report["unsafe_item_count"] == 1


def test_merge_readiness_bridge_blocks_non_ready_item():
    rows = default_merge_readiness_items()
    rows[0]["status"] = "not_ready"

    report = build_merge_readiness_bridge("p13-operator-console", "main", rows)

    assert report["readiness_status"] == "BLOCKED_NON_READY_ITEM"
    assert report["non_ready_item_count"] == 1


def test_merge_readiness_bridge_preserves_safety_boundary():
    report = build_merge_readiness_bridge(
        "p13-operator-console",
        "main",
        default_merge_readiness_items(),
    )

    assert report["paper_only"] is True
    assert report["local_only"] is True
    assert report["operator_review_required"] is True
    assert report["real_world_actions_allowed"] is False
    assert report["real_execution"] is False


def test_merge_readiness_bridge_rejects_same_branch():
    with pytest.raises(ValueError, match="source_branch and target_branch must differ"):
        build_merge_readiness_bridge("main", "main", default_merge_readiness_items())


def test_write_merge_readiness_bridge_creates_json(tmp_path):
    output = tmp_path / "p14_merge_readiness_bridge.json"

    result = write_merge_readiness_bridge(
        "p13-operator-console",
        "main",
        default_merge_readiness_items(),
        output,
    )

    assert result["ok"] is True
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["type"] == "p14_merge_readiness_bridge"
    assert data["merge_policy"]["merge_auto_apply_allowed"] is False
