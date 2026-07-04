import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_p46_final_state_handoff import build_p46_architecture_index
from btc_finance_platform.paper_p46_final_state_handoff import build_p46_final_project_state
from btc_finance_platform.paper_p46_final_state_handoff import build_p46_final_state_closeout
from btc_finance_platform.paper_p46_final_state_handoff import build_p46_handoff_packet

def test_p46_final_project_state_uses_1005_baseline():
    result = build_p46_final_project_state()
    assert result["phase"] == "P46"
    assert result["step_range"] == "D1-D3"
    assert result["baseline_tests"] == 1005
    assert result["current_state_recorded"] is True

def test_p46_final_project_state_records_p45_lock():
    result = build_p46_final_project_state()
    assert result["previous_phase"] == "P45"
    assert result["p45_final_acceptance_locked"] is True

def test_p46_final_project_state_blocks_release_deploy():
    result = build_p46_final_project_state()
    assert result["tag_allowed"] is False
    assert result["release_allowed"] is False
    assert result["deploy_allowed"] is False
    assert result["real_world_actions_allowed"] is False

def test_p46_handoff_packet_uses_1008_baseline():
    result = build_p46_handoff_packet()
    assert result["phase"] == "P46"
    assert result["step_range"] == "D4-D6"
    assert result["baseline_tests"] == 1008
    assert result["handoff_ready"] is True

def test_p46_handoff_packet_records_latest_count():
    result = build_p46_handoff_packet()
    assert result["latest_known_passed_count"] == 1005
    assert result["next_window_recoverable"] is True

def test_p46_handoff_packet_points_to_p47():
    result = build_p46_handoff_packet()
    assert result["next_phase"] == "P47 final consistency audit"
    assert result["operator_review_required"] is True

def test_p46_architecture_index_uses_1011_baseline():
    result = build_p46_architecture_index()
    assert result["phase"] == "P46"
    assert result["step_range"] == "D7-D9"
    assert result["baseline_tests"] == 1011
    assert result["index_ready"] is True

def test_p46_architecture_index_covers_p31_to_p45():
    result = build_p46_architecture_index()
    assert result["covered_range"] == "P31-P45"
    assert "final_governance" in result["core_layers"]

def test_p46_architecture_index_has_core_layers():
    result = build_p46_architecture_index()
    assert "local_data" in result["core_layers"]
    assert "learning_engine" in result["core_layers"]
    assert "operator_console" in result["core_layers"]

def test_p46_final_state_closeout_uses_1014_baseline():
    result = build_p46_final_state_closeout()
    assert result["phase"] == "P46"
    assert result["step_range"] == "D10-D12"
    assert result["baseline_tests"] == 1014
    assert result["p46_complete"] is True

def test_p46_final_state_closeout_points_to_p47():
    result = build_p46_final_state_closeout()
    assert result["ready_for_p47_consistency_audit"] is True
    assert result["ready_for_new_functional_expansion"] is False

def test_p46_final_state_closeout_blocks_release_deploy():
    result = build_p46_final_state_closeout()
    assert result["ready_for_tag"] is False
    assert result["ready_for_release"] is False
    assert result["ready_for_deploy"] is False
    assert result["real_world_actions_allowed"] is False
