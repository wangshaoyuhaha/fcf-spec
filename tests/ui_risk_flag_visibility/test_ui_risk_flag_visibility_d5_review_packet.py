from app.ui_risk_flag_visibility.visibility_review_packet import build_visibility_review_packet


def test_ui_risk_flag_visibility_d5_review_packet():
    packet = build_visibility_review_packet()
    assert packet["packet_id"] == "UI-RISK-FLAG-VISIBILITY-APP-1-D5"
    assert packet["review_status"] == "VISIBILITY_REVIEW_PASS"
    assert packet["risk_flags_visible"] is True
    assert packet["reason_codes_visible"] is True
    assert packet["blocked_response_state_visible"] is True
    assert packet["operator_review_required_visible"] is True
    assert packet["risk_flag_downgrade_allowed"] is False
    assert packet["risk_flag_deletion_allowed"] is False
    assert packet["reason_code_deletion_allowed"] is False
    assert packet["reason_code_mutation_allowed"] is False
    assert packet["warning_to_approval_conversion_allowed"] is False
    assert packet["operator_review_bypass_allowed"] is False
    assert packet["ui_approval_override_allowed"] is False
    assert packet["paper_only"] is True
    assert packet["local_only"] is True
    assert packet["read_only"] is True
    assert packet["sidecar_only"] is True
    assert packet["trade_action_allowed"] is False
    assert packet["real_execution_allowed"] is False
    assert packet["buy_button_enabled"] is False
    assert packet["sell_button_enabled"] is False
    assert packet["order_button_enabled"] is False
    assert packet["tag_allowed"] is False
    assert packet["release_allowed"] is False
    assert packet["deploy_allowed"] is False
