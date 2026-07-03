import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_learning_engine_closeout import REQUIRED_MODULE_KEYS
from btc_finance_platform.p14_learning_engine_closeout import build_learning_engine_closeout_report
from btc_finance_platform.p14_learning_engine_closeout import default_p14_closeout_modules
from btc_finance_platform.p14_learning_engine_closeout import normalize_closeout_module
from btc_finance_platform.p14_learning_engine_closeout import write_learning_engine_closeout_report


def test_default_p14_closeout_modules_cover_required_keys():
    keys = {row["module_key"] for row in default_p14_closeout_modules()}

    assert set(REQUIRED_MODULE_KEYS) == keys


def test_learning_engine_closeout_ready_for_operator_review():
    report = build_learning_engine_closeout_report(default_p14_closeout_modules())

    assert report["closeout_status"] == "READY_FOR_OPERATOR_REVIEW"
    assert report["required_module_count"] == 13
    assert report["missing_modules"] == []


def test_learning_engine_closeout_blocks_missing_required_module():
    rows = [
        row for row in default_p14_closeout_modules()
        if row["module_key"] != "scenario_engine"
    ]

    report = build_learning_engine_closeout_report(rows)

    assert report["closeout_status"] == "BLOCKED_MISSING_REQUIRED_MODULES"
    assert "scenario_engine" in report["missing_modules"]


def test_learning_engine_closeout_blocks_unsafe_module():
    rows = default_p14_closeout_modules()
    rows[0]["auto_apply_allowed"] = True

    report = build_learning_engine_closeout_report(rows)

    assert report["closeout_status"] == "BLOCKED_SAFETY_BOUNDARY_VIOLATION"
    assert report["unsafe_module_count"] == 1


def test_learning_engine_closeout_preserves_safety_boundary():
    report = build_learning_engine_closeout_report(default_p14_closeout_modules())

    assert report["paper_only"] is True
    assert report["local_only"] is True
    assert report["operator_review_required"] is True
    assert report["real_world_actions_allowed"] is False
    assert report["real_execution"] is False


def test_normalize_closeout_module_requires_module_key():
    with pytest.raises(ValueError, match="module_key is required"):
        normalize_closeout_module({"stage": "P14-D1-D3"})


def test_write_learning_engine_closeout_report_creates_json(tmp_path):
    output = tmp_path / "p14_learning_engine_closeout_report.json"

    result = write_learning_engine_closeout_report(
        default_p14_closeout_modules(),
        output,
    )

    assert result["ok"] is True
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["type"] == "p14_learning_engine_closeout_report"
    assert data["closeout_policy"]["auto_apply_allowed"] is False
