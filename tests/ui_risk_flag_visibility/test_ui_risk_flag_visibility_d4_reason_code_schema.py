from app.ui_risk_flag_visibility.reason_code_schema import build_reason_code_visibility_schema


def test_ui_risk_flag_visibility_d4_reason_code_schema():
    schema = build_reason_code_visibility_schema()
    assert schema["schema_id"] == "UI-RISK-FLAG-VISIBILITY-APP-1-D4"
    assert schema["reason_codes_required"] is True
    assert schema["reason_codes_rendered_explicitly"] is True
    assert schema["reason_code_source_visible"] is True
    assert schema["reason_code_count_visible"] is True
    assert schema["reason_code_meaning_visible"] is True
    assert schema["reason_code_deletion_allowed"] is False
    assert schema["reason_code_mutation_allowed"] is False
    assert schema["reason_code_silencing_allowed"] is False
    assert schema["risk_flag_downgrade_allowed"] is False
    assert schema["warning_to_approval_conversion_allowed"] is False
    assert schema["operator_review_required_visible"] is True
    assert schema["operator_review_bypass_allowed"] is False
    assert schema["paper_only"] is True
    assert schema["local_only"] is True
    assert schema["read_only"] is True
    assert schema["sidecar_only"] is True
    assert schema["trade_action_allowed"] is False
    assert schema["real_execution_allowed"] is False
    assert schema["buy_button_enabled"] is False
    assert schema["sell_button_enabled"] is False
    assert schema["order_button_enabled"] is False
