from app.ui_risk_flag_visibility.final_handoff import build_final_handoff


def test_ui_risk_flag_visibility_d6_final_handoff():
    handoff = build_final_handoff()
    assert handoff["app_id"] == "UI-RISK-FLAG-VISIBILITY-APP-1"
    assert handoff["stage"] == "D6_FINAL_HANDOFF_CLOSEOUT"
    assert handoff["final_status"] == "COMPLETED"
    assert handoff["source_packet_id"] == "UI-RISK-FLAG-VISIBILITY-APP-1-D5"
    assert handoff["risk_flags_visible"] is True
    assert handoff["reason_codes_visible"] is True
    assert handoff["blocked_response_state_visible"] is True
    assert handoff["operator_review_required_visible"] is True
    assert handoff["risk_flag_downgrade_allowed"] is False
    assert handoff["risk_flag_deletion_allowed"] is False
    assert handoff["reason_code_deletion_allowed"] is False
    assert handoff["operator_review_bypass_allowed"] is False
    assert handoff["ui_approval_override_allowed"] is False
    assert handoff["paper_only"] is True
    assert handoff["local_only"] is True
    assert handoff["read_only"] is True
    assert handoff["sidecar_only"] is True
    assert handoff["trade_action_allowed"] is False
    assert handoff["real_execution_allowed"] is False
    assert handoff["buy_button_enabled"] is False
    assert handoff["sell_button_enabled"] is False
    assert handoff["order_button_enabled"] is False
    assert handoff["tag_allowed"] is False
    assert handoff["release_allowed"] is False
    assert handoff["deploy_allowed"] is False
