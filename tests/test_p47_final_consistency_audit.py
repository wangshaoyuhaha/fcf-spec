import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_p47_final_consistency_audit import build_p47_final_consistency_closeout
from btc_finance_platform.paper_p47_final_consistency_audit import build_p47_phase_file_matrix
from btc_finance_platform.paper_p47_final_consistency_audit import build_p47_safety_boundary_audit
from btc_finance_platform.paper_p47_final_consistency_audit import build_p47_serialization_audit

def test_p47_phase_file_matrix_uses_1017_baseline():
    result = build_p47_phase_file_matrix()
    assert result["phase"] == "P47"
    assert result["step_range"] == "D1-D3"
    assert result["baseline_tests"] == 1017

def test_p47_phase_file_matrix_covers_recent_closeout_phases():
    result = build_p47_phase_file_matrix()
    assert result["covered_phases"] == ["P43", "P44", "P45", "P46"]
    assert result["audit_ready"] is True

def test_p47_phase_file_matrix_requires_four_file_classes():
    result = build_p47_phase_file_matrix()
    assert result["required_suffixes"] == ["docs", "scripts", "src", "tests"]
    assert result["operator_review_required"] is True

def test_p47_serialization_audit_uses_1020_baseline():
    result = build_p47_serialization_audit()
    assert result["payload"]["phase"] == "P47"
    assert result["payload"]["step_range"] == "D4-D6"
    assert result["payload"]["baseline_tests"] == 1020

def test_p47_serialization_audit_is_stable():
    result = build_p47_serialization_audit()
    assert result["stable_json"] == result["stable_json_repeat"]

def test_p47_serialization_audit_is_json_loadable():
    result = build_p47_serialization_audit()
    loaded = json.loads(result["stable_json"])
    assert loaded["artifact"] == "serialization_audit"
    assert loaded["stable_serialization_required"] is True

def test_p47_safety_boundary_uses_1023_baseline():
    result = build_p47_safety_boundary_audit()
    assert result["phase"] == "P47"
    assert result["step_range"] == "D7-D9"
    assert result["baseline_tests"] == 1023

def test_p47_safety_boundary_preserves_paper_local_read_only():
    result = build_p47_safety_boundary_audit()
    assert result["paper_only"] is True
    assert result["local_only"] is True
    assert result["read_only"] is True

def test_p47_safety_boundary_blocks_release_deploy_real_actions():
    result = build_p47_safety_boundary_audit()
    assert result["tag_allowed"] is False
    assert result["release_allowed"] is False
    assert result["deploy_allowed"] is False
    assert result["real_world_actions_allowed"] is False

def test_p47_final_consistency_closeout_uses_1026_baseline():
    result = build_p47_final_consistency_closeout()
    assert result["phase"] == "P47"
    assert result["step_range"] == "D10-D12"
    assert result["baseline_tests"] == 1026

def test_p47_final_consistency_closeout_stops_functional_expansion():
    result = build_p47_final_consistency_closeout()
    assert result["p47_complete"] is True
    assert result["new_functional_expansion_allowed"] is False
    assert result["ready_for_final_handoff"] is True

def test_p47_final_consistency_closeout_blocks_release_deploy():
    result = build_p47_final_consistency_closeout()
    assert result["ready_for_tag"] is False
    assert result["ready_for_release"] is False
    assert result["ready_for_deploy"] is False
    assert result["operator_review_required"] is True
