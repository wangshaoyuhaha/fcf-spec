from apps.dify_ui_handoff_app_1.final_closeout import (
    COMPLETED_STAGES,
    SAFETY,
    STAGE_ID,
    build_final_closeout,
    summarize_final_closeout,
    validate_final_closeout,
)

def test_d6_final_closeout_status():
    closeout = build_final_closeout()
    assert closeout["stage_id"] == STAGE_ID
    assert closeout["status"] == "completed"
    assert closeout["ready_for_operator_merge_review"] is True

def test_d6_completed_stages():
    closeout = build_final_closeout()
    assert len(closeout["completed_stages"]) == 6
    for stage in COMPLETED_STAGES:
        assert stage in closeout["completed_stages"]

def test_d6_prompt_and_guide_valid():
    closeout = build_final_closeout()
    assert closeout["prompt_summary"]["valid"] is True
    assert closeout["manual_workflow_guide_summary"]["valid"] is True

def test_d6_safety_boundary_locked():
    closeout = build_final_closeout()
    for key, value in SAFETY.items():
        assert closeout["safety"][key] is value

def test_d6_no_merge_release_deploy():
    closeout = build_final_closeout()
    assert closeout["auto_merge_allowed"] is False
    assert closeout["release_allowed"] is False
    assert closeout["deploy_allowed"] is False

def test_d6_validation_passes():
    validation = validate_final_closeout()
    assert validation["valid"] is True
    assert validation["issues"] == []
    assert validation["stage_id"] == STAGE_ID

def test_d6_summary_safe():
    summary = summarize_final_closeout()
    assert summary["valid"] is True
    assert summary["completed_stage_count"] == 6
    assert summary["paper_only"] is True
    assert summary["local_only"] is True
    assert summary["read_only"] is True
    assert summary["operator_review_required"] is True
    assert summary["real_execution_allowed"] is False
    assert summary["trade_action_enabled"] is False
    assert summary["auto_merge_allowed"] is False
    assert summary["release_allowed"] is False
    assert summary["deploy_allowed"] is False
