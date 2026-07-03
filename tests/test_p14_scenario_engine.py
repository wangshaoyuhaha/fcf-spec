import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_scenario_engine import build_scenario_engine_report
from btc_finance_platform.p14_scenario_engine import classify_scenario_result
from btc_finance_platform.p14_scenario_engine import evaluate_scenario
from btc_finance_platform.p14_scenario_engine import write_scenario_engine_report


def test_classify_scenario_result_passes_good_case():
    assert classify_scenario_result(0.05, 0.04) == "pass"


def test_classify_scenario_result_warns_negative_return():
    assert classify_scenario_result(-0.02, 0.05) == "warn"


def test_classify_scenario_result_fails_high_drawdown():
    assert classify_scenario_result(0.05, 0.35) == "fail"


def test_evaluate_scenario_preserves_paper_only_boundary():
    result = evaluate_scenario(
        {
            "scenario_id": "trend_up_normal",
            "paper_return_pct": 0.05,
            "max_paper_drawdown_pct": 0.04,
        }
    )

    assert result["paper_only"] is True
    assert result["local_only"] is True
    assert result["operator_review_required"] is True
    assert result["real_world_actions_allowed"] is False
    assert result["real_execution"] is False


def test_scenario_engine_report_blocks_on_failure():
    report = build_scenario_engine_report(
        "proposal_001",
        [
            {
                "scenario_id": "critical_drawdown",
                "paper_return_pct": 0.02,
                "max_paper_drawdown_pct": 0.35,
            }
        ],
    )

    assert report["report_status"] == "BLOCKED_BY_SCENARIO_FAILURE"
    assert report["fail_count"] == 1
    assert report["scenario_policy"]["auto_accept_allowed"] is False


def test_scenario_engine_rejects_missing_proposal_id():
    with pytest.raises(ValueError, match="proposal_id is required"):
        build_scenario_engine_report("", [{"scenario_id": "x"}])


def test_write_scenario_engine_report_creates_json(tmp_path):
    output = tmp_path / "scenario_engine_report.json"

    result = write_scenario_engine_report(
        "proposal_001",
        [
            {
                "scenario_id": "normal",
                "paper_return_pct": 0.04,
                "max_paper_drawdown_pct": 0.03,
            }
        ],
        output,
    )

    assert result["ok"] is True
    assert output.exists()

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["type"] == "p14_scenario_engine_report"
    assert data["scenario_policy"]["auto_accept_allowed"] is False
