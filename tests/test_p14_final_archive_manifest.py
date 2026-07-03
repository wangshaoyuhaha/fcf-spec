import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_final_archive_manifest import REQUIRED_ARCHIVE_ITEMS
from btc_finance_platform.p14_final_archive_manifest import build_final_archive_manifest
from btc_finance_platform.p14_final_archive_manifest import default_final_archive_items
from btc_finance_platform.p14_final_archive_manifest import normalize_archive_item
from btc_finance_platform.p14_final_archive_manifest import write_final_archive_manifest


def test_default_final_archive_items_cover_required_keys():
    keys = {row["item_key"] for row in default_final_archive_items()}

    assert set(REQUIRED_ARCHIVE_ITEMS) == keys


def test_final_archive_manifest_ready_for_operator_archive_review():
    manifest = build_final_archive_manifest(
        "p13-operator-console",
        "main",
        591,
        default_final_archive_items(),
    )

    assert manifest["archive_status"] == "READY_FOR_FINAL_OPERATOR_ARCHIVE_REVIEW"
    assert manifest["archive_policy"]["merge_to_main_allowed_now"] is False


def test_final_archive_manifest_blocks_missing_item():
    rows = [
        row for row in default_final_archive_items()
        if row["item_key"] != "p14_final_operator_acceptance_packet"
    ]

    manifest = build_final_archive_manifest("p13-operator-console", "main", 591, rows)

    assert manifest["archive_status"] == "BLOCKED_MISSING_ARCHIVE_ITEM"
    assert "p14_final_operator_acceptance_packet" in manifest["missing_items"]


def test_final_archive_manifest_blocks_unsafe_item():
    rows = default_final_archive_items()
    rows[0]["archive_auto_publish_allowed"] = True

    manifest = build_final_archive_manifest("p13-operator-console", "main", 591, rows)

    assert manifest["archive_status"] == "BLOCKED_SAFETY_BOUNDARY_VIOLATION"
    assert manifest["unsafe_item_count"] == 1


def test_final_archive_manifest_blocks_non_archived_item():
    rows = default_final_archive_items()
    rows[0]["status"] = "pending"

    manifest = build_final_archive_manifest("p13-operator-console", "main", 591, rows)

    assert manifest["archive_status"] == "BLOCKED_NON_ARCHIVED_ITEM"
    assert manifest["non_archived_item_count"] == 1


def test_final_archive_manifest_preserves_safety_boundary():
    manifest = build_final_archive_manifest(
        "p13-operator-console",
        "main",
        591,
        default_final_archive_items(),
    )

    assert manifest["paper_only"] is True
    assert manifest["local_only"] is True
    assert manifest["operator_review_required"] is True
    assert manifest["real_world_actions_allowed"] is False
    assert manifest["real_execution"] is False


def test_write_final_archive_manifest_creates_json(tmp_path):
    output = tmp_path / "p14_final_archive_manifest.json"

    result = write_final_archive_manifest(
        "p13-operator-console",
        "main",
        591,
        default_final_archive_items(),
        output,
    )

    assert result["ok"] is True
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["type"] == "p14_final_archive_manifest"
    assert data["archive_policy"]["archive_auto_publish_allowed"] is False
