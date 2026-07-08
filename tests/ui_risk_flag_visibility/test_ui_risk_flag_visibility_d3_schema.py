from app.ui_risk_flag_visibility.risk_flag_schema import build_risk_flag_visibility_schema


def test_ui_risk_flag_visibility_d3_schema():
    schema = build_risk_flag_visibility_schema()
    assert schema["schema_id"] == "UI-RISK-FLAG-VISIBILITY-APP-1-D3"
    assert schema["risk_flags_required"] is True
    assert schema["risk_flags_rendered_explicitly"] is True
    assert schema["risk_flag_severity_visible"] is True
    assert schema["risk_flag_source_visible"] is True
    assert schema["risk_flag_count_visible"] is True
    assert schema["risk_flag_downgrade_allowed"] is False
    assert schema["risk_flag_deletion_allowed"] is False
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
