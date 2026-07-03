import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p13_final_closeout_summary import build_p13_final_closeout_summary
from btc_finance_platform.p13_final_closeout_summary import write_p13_final_closeout_summary


def test_p13_final_closeout_ready_for_manual_merge_review(tmp_path):
    summary = build_p13_final_closeout_summary(
        tmp_path / "index.html",
        tmp_path / "missing_ledger.json",
    )

    assert summary["p13_final_status"] == "READY_FOR_MANUAL_MAIN_MERGE_REVIEW"
    assert summary["p13_completed"] is True
    assert summary["merge_to_main_completed"] is False
    assert summary["release_created"] is False


def test_p13_final_closeout_preserves_safety_boundary(tmp_path):
    summary = build_p13_final_closeout_summary(
        tmp_path / "index.html",
        tmp_path / "missing_ledger.json",
    )

    assert summary["paper_only"] is True
    assert summary["local_only"] is True
    assert summary["ui_mode"] == "read_only"
    assert summary["operator_review_required"] is True
    assert summary["real_world_actions_allowed"] is False
    assert summary["real_execution"] is False


def test_p13_final_closeout_blocks_auto_patch_merge_release(tmp_path):
    summary = build_p13_final_closeout_summary(
        tmp_path / "index.html",
        tmp_path / "missing_ledger.json",
    )

    assert summary["patch_auto_apply_allowed"] is False
    assert summary["auto_merge_allowed"] is False
    assert summary["auto_release_allowed"] is False
    assert summary["deployment_allowed_now"] is False


def test_p13_final_closeout_lists_all_units(tmp_path):
    summary = build_p13_final_closeout_summary(
        tmp_path / "index.html",
        tmp_path / "missing_ledger.json",
    )

    assert "P13-D1-D3 read-only operator console skeleton" in summary["completed_units"]
    assert "P13-D22-D24 AI learning memory ledger" in summary["completed_units"]
    assert "P13-D28-D30 final closeout summary" in summary["completed_units"]


def test_write_p13_final_closeout_summary_creates_json(tmp_path):
    output = tmp_path / "index.html"
    ledger = tmp_path / "missing_ledger.json"
    summary_path = tmp_path / "p13_final_closeout_summary.json"

    result = write_p13_final_closeout_summary(output, ledger, summary_path)

    assert result["ok"] is True
    assert summary_path.exists()

    data = json.loads(summary_path.read_text(encoding="utf-8"))
    assert data["type"] == "p13_final_closeout_summary"
    assert data["merge_to_main_completed"] is False
    assert data["release_created"] is False
