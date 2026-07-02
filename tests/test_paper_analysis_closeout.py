import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_analysis_closeout import build_p4_closeout_package
from btc_finance_platform.paper_analysis_closeout import get_p4_analysis_layer_capabilities
from btc_finance_platform.paper_analysis_closeout import get_p4_safety_acceptance
from btc_finance_platform.paper_analysis_closeout import get_p4_to_p5_transition_anchor


JSON_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.json"
CSV_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.csv"
SOURCES = [JSON_FIXTURE, CSV_FIXTURE]


def test_p4_analysis_layer_capabilities_marks_p4_completed():
    result = get_p4_analysis_layer_capabilities()

    assert result["ok"] is True
    assert result["type"] == "p4_analysis_layer_capabilities"
    assert result["phase"] == "P4"
    assert result["status"] == "completed"
    assert len(result["completed_scope"]) == 15


def test_p4_capabilities_include_pipeline_review_and_report():
    result = get_p4_analysis_layer_capabilities()

    assert "P3 handoff to P4 analysis pipeline" in result["capabilities"]
    assert "operator review packet" in result["capabilities"]
    assert "human-readable markdown report" in result["capabilities"]
    assert result["broader_goal"] == "general FCF-style finance platform for stocks and other markets"


def test_p4_safety_acceptance_passes_all_checks():
    result = get_p4_safety_acceptance()

    assert result["ok"] is True
    assert result["type"] == "p4_safety_acceptance"
    assert result["decision"] == "P4 accepted for paper-only analysis-layer closeout"
    assert all(result["checks"].values())


def test_p4_safety_acceptance_preserves_no_real_world_effects():
    result = get_p4_safety_acceptance()

    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_api_key_required"] is False
    assert result["wallet_private_key_required"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_balance"] is False
    assert result["real_position"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True


def test_p4_to_p5_transition_anchor_names_next_phase():
    result = get_p4_to_p5_transition_anchor()

    assert result["ok"] is True
    assert result["type"] == "p4_to_p5_transition_anchor"
    assert result["from_phase"] == "P4 paper analysis logic enhancement"
    assert result["to_phase"] == "P5 risk governance and regime layer"
    assert "risk governor baseline" in result["p5_candidate_scope"]


def test_p4_to_p5_transition_anchor_preserves_fcf_direction():
    result = get_p4_to_p5_transition_anchor()

    assert "FCF-style event-driven architecture direction" in result["must_preserve"]
    assert "operator review required" in result["must_preserve"]
    assert "no real orders" in result["must_preserve"]


def test_build_p4_closeout_package():
    result = build_p4_closeout_package(SOURCES)

    assert result["ok"] is True
    assert result["type"] == "p4_closeout_package"
    assert result["phase"] == "P4"
    assert result["status"] == "completed"
    assert result["next_phase"] == "P5 risk governance and regime layer"
    assert result["decision"] == "P4_closed_paper_only_ready_for_P5"


def test_p4_closeout_package_preserves_safety_flags():
    result = build_p4_closeout_package(SOURCES)

    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_api_key_required"] is False
    assert result["wallet_private_key_required"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_balance"] is False
    assert result["real_position"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True
