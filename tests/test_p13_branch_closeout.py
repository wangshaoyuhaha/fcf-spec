import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p13_branch_closeout import build_p13_branch_closeout_manifest
from btc_finance_platform.p13_branch_closeout import write_p13_branch_closeout_manifest


def test_p13_branch_closeout_ready_for_review(tmp_path):
    manifest = build_p13_branch_closeout_manifest(tmp_path / "index.html")

    assert manifest["closeout_status"] == "READY_FOR_BRANCH_REVIEW"
    assert manifest["ready_for_main_merge_review"] is True
    assert manifest["merge_to_main_completed"] is False
    assert manifest["release_created"] is False


def test_p13_branch_closeout_preserves_safety_boundary(tmp_path):
    manifest = build_p13_branch_closeout_manifest(tmp_path / "index.html")

    assert manifest["paper_only"] is True
    assert manifest["local_only"] is True
    assert manifest["ui_mode"] == "read_only"
    assert manifest["operator_review_required"] is True
    assert manifest["trading_buttons_enabled"] is False
    assert manifest["real_world_actions_allowed"] is False


def test_p13_branch_closeout_lists_completed_units(tmp_path):
    manifest = build_p13_branch_closeout_manifest(tmp_path / "index.html")

    assert "P13-D1-D3 read-only operator console skeleton" in manifest["completed_p13_units"]
    assert "P13-D13-D15 operator console acceptance summary" in manifest["completed_p13_units"]
    assert "P13-D16-D18 branch closeout manifest" in manifest["completed_p13_units"]


def test_write_p13_branch_closeout_manifest_creates_json(tmp_path):
    output = tmp_path / "index.html"
    manifest_path = tmp_path / "p13_branch_closeout_manifest.json"

    result = write_p13_branch_closeout_manifest(output, manifest_path)

    assert result["ok"] is True
    assert manifest_path.exists()

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data["type"] == "p13_branch_closeout_manifest"
    assert data["merge_to_main_completed"] is False
    assert data["release_created"] is False
