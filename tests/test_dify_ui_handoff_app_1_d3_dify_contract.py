from apps.dify_ui_handoff_app_1.dify_contract import (
    REQUIRED_OUTPUT_SECTIONS,
    build_safe_blocked_response,
    get_dify_input_contract,
    get_dify_io_contract,
    get_dify_output_contract,
    summarize_dify_io_contract,
    validate_dify_input_payload,
    validate_dify_output_response,
)


def test_dify_ui_handoff_d3_input_contract_is_safe():
    contract = get_dify_input_contract()

    assert contract["stage_id"] == "DIFY-UI-HANDOFF-D3"
    assert contract["paper_only"] is True
    assert contract["local_only"] is True
    assert contract["read_only"] is True
    assert contract["operator_review_required"] is True
    assert contract["manual_dify_configuration_required"] is True
    assert contract["automated_dify_app_creation_allowed"] is False
    assert contract["dify_api_write_allowed"] is False

    fields = {field["name"] for field in contract["input_fields"]}
    assert "operator_question" in fields
    assert "fcf_report_text" in fields
    assert "fcf_manifest_text" in fields
    assert "review_context" in fields
    assert "paper_only_ack" in fields


def test_dify_ui_handoff_d3_output_contract_blocks_real_world_actions():
    contract = get_dify_output_contract()

    assert contract["paper_only"] is True
    assert contract["local_only"] is True
    assert contract["read_only"] is True
    assert contract["operator_review_required"] is True
    assert contract["real_execution_allowed"] is False
    assert contract["trade_action_enabled"] is False
    assert contract["buy_button_enabled"] is False
    assert contract["sell_button_enabled"] is False
    assert contract["order_button_enabled"] is False
    assert contract["operator_review_bypass_allowed"] is False
    assert contract["risk_flag_downgrade_allowed"] is False
    assert contract["reason_code_mutation_allowed"] is False

    blocked_actions = set(contract["output_contract"]["blocked_actions"])
    assert "buy" in blocked_actions
    assert "sell" in blocked_actions
    assert "place order" in blocked_actions
    assert "connect exchange" in blocked_actions
    assert "request api key" in blocked_actions


def test_dify_ui_handoff_d3_combined_contract_has_sources():
    contract = get_dify_io_contract()

    assert contract["paper_only"] is True
    assert contract["local_only"] is True
    assert contract["read_only"] is True
    assert contract["operator_review_required"] is True
    assert contract["source_manifest_summary"]["source_count"] > 0
    assert contract["source_manifest_summary"]["missing_source_count"] == 0


def test_dify_ui_handoff_d3_validates_good_input_payload():
    payload = {
        "operator_question": "Summarize the local FCF report for review.",
        "fcf_report_text": "paper-only report",
        "fcf_manifest_text": "local manifest",
        "review_context": "operator review",
        "paper_only_ack": True,
    }

    validation = validate_dify_input_payload(payload)

    assert validation["valid"] is True
    assert validation["issues"] == []
    assert validation["blocked"] is False


def test_dify_ui_handoff_d3_blocks_real_trading_input_payload():
    payload = {
        "operator_question": "Buy now and place order using my api key.",
        "fcf_report_text": "",
        "fcf_manifest_text": "",
        "review_context": "",
        "paper_only_ack": True,
    }

    validation = validate_dify_input_payload(payload)

    assert validation["valid"] is False
    assert validation["blocked"] is True
    assert "buy now" in validation["blocked_matches"]
    assert "place order" in validation["blocked_matches"]
    assert "api key" in validation["blocked_matches"]


def test_dify_ui_handoff_d3_requires_paper_only_ack():
    payload = {
        "operator_question": "Summarize report.",
        "paper_only_ack": False,
    }

    validation = validate_dify_input_payload(payload)

    assert validation["valid"] is False
    assert "paper_only_ack must be true" in validation["issues"]


def test_dify_ui_handoff_d3_validates_output_response():
    response = {
        "paper_only": True,
        "operator_review_required": True,
        "real_execution_allowed": False,
        "trade_action_enabled": False,
        "sections": {section: "ok" for section in REQUIRED_OUTPUT_SECTIONS},
    }

    validation = validate_dify_output_response(response)

    assert validation["valid"] is True
    assert validation["issues"] == []


def test_dify_ui_handoff_d3_blocks_bad_output_response():
    response = {
        "paper_only": True,
        "operator_review_required": True,
        "real_execution_allowed": False,
        "trade_action_enabled": False,
        "sections": {section: "ok" for section in REQUIRED_OUTPUT_SECTIONS},
        "unsafe": "buy now and execute trade",
    }

    validation = validate_dify_output_response(response)

    assert validation["valid"] is False
    assert "buy now" in validation["forbidden_hits"]
    assert "execute trade" in validation["forbidden_hits"]


def test_dify_ui_handoff_d3_safe_blocked_response_is_complete():
    response = build_safe_blocked_response(
        reason="real trading request",
        operator_question="buy now",
    )

    validation = validate_dify_output_response(response)

    assert response["status"] == "BLOCKED_UNSAFE_OR_REAL_WORLD_REQUEST"
    assert response["paper_only"] is True
    assert response["local_only"] is True
    assert response["read_only"] is True
    assert response["operator_review_required"] is True
    assert response["real_execution_allowed"] is False
    assert response["trade_action_enabled"] is False
    assert validation["valid"] is True
    assert "REAL_WORLD_ACTION_REQUEST_BLOCKED" in response["sections"]["risk_flags"]


def test_dify_ui_handoff_d3_summary_is_safe():
    summary = summarize_dify_io_contract()

    assert summary["stage_id"] == "DIFY-UI-HANDOFF-D3"
    assert summary["input_field_count"] == 5
    assert summary["required_output_section_count"] == len(REQUIRED_OUTPUT_SECTIONS)
    assert summary["source_count"] > 0
    assert summary["missing_source_count"] == 0
    assert summary["paper_only"] is True
    assert summary["local_only"] is True
    assert summary["read_only"] is True
    assert summary["operator_review_required"] is True
    assert summary["real_execution_allowed"] is False
    assert summary["trade_action_enabled"] is False
