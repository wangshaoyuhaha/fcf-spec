from apps.dify_ui_handoff_app_1.dify_contract import REQUIRED_OUTPUT_SECTIONS
from apps.dify_ui_handoff_app_1.manual_workflow_guide import (
    BLOCKED_CONFIGURATION_ITEMS,
    REQUIRED_VARIABLES,
    STAGE_ID,
    build_dify_manual_workflow_guide,
    summarize_dify_manual_workflow_guide,
    validate_dify_manual_workflow_guide,
)


def test_dify_ui_handoff_d5_guide_is_safe():
    guide = build_dify_manual_workflow_guide()

    assert guide["stage_id"] == STAGE_ID
    assert guide["paper_only"] is True
    assert guide["local_only"] is True
    assert guide["read_only"] is True
    assert guide["sidecar_only"] is True
    assert guide["operator_review_required"] is True
    assert guide["manual_configuration_only"] is True
    assert guide["automated_dify_app_creation_allowed"] is False
    assert guide["dify_api_write_allowed"] is False
    assert guide["real_execution_allowed"] is False
    assert guide["trade_action_enabled"] is False


def test_dify_ui_handoff_d5_required_variables_are_present():
    guide = build_dify_manual_workflow_guide()
    variables = {item["name"]: item for item in guide["required_variables"]}

    assert "operator_question" in variables
    assert "fcf_report_text" in variables
    assert "fcf_manifest_text" in variables
    assert "review_context" in variables
    assert "paper_only_ack" in variables
    assert variables["paper_only_ack"]["required"] is True
    assert len(REQUIRED_VARIABLES) == 5


def test_dify_ui_handoff_d5_workflow_steps_are_manual_only():
    guide = build_dify_manual_workflow_guide()

    assert len(guide["manual_workflow_steps"]) >= 6

    joined = " ".join(
        step["operator_action"] + " " + step["required_setting"]
        for step in guide["manual_workflow_steps"]
    ).lower()

    assert "manual" in joined
    assert "no external tool" in joined
    assert "no plugin" in joined
    assert "no api write" in joined
    assert "no automatic approval" in joined
    assert "no real-world execution" in joined


def test_dify_ui_handoff_d5_blocks_unsafe_configuration_items():
    guide = build_dify_manual_workflow_guide()
    blocked = set(guide["blocked_configuration_items"])

    for item in BLOCKED_CONFIGURATION_ITEMS:
        assert item in blocked

    assert "dify_api_write" in blocked
    assert "automatic_app_creation" in blocked
    assert "broker_connection" in blocked
    assert "exchange_connection" in blocked
    assert "api_key_variable" in blocked
    assert "wallet_private_key_variable" in blocked
    assert "order_execution_node" in blocked
    assert "trade_action_button" in blocked
    assert "operator_review_bypass" in blocked


def test_dify_ui_handoff_d5_required_output_sections_are_preserved():
    guide = build_dify_manual_workflow_guide()

    for section in REQUIRED_OUTPUT_SECTIONS:
        assert section in guide["required_output_sections"]


def test_dify_ui_handoff_d5_validation_passes():
    validation = validate_dify_manual_workflow_guide()

    assert validation["valid"] is True
    assert validation["issues"] == []
    assert validation["stage_id"] == STAGE_ID
    assert validation["required_variable_count"] == 5
    assert validation["workflow_step_count"] >= 6
    assert validation["blocked_configuration_count"] == len(BLOCKED_CONFIGURATION_ITEMS)


def test_dify_ui_handoff_d5_summary_is_safe():
    summary = summarize_dify_manual_workflow_guide()

    assert summary["stage_id"] == STAGE_ID
    assert summary["valid"] is True
    assert summary["required_variable_count"] == 5
    assert summary["workflow_step_count"] >= 6
    assert summary["blocked_configuration_count"] == len(BLOCKED_CONFIGURATION_ITEMS)
    assert summary["paper_only"] is True
    assert summary["local_only"] is True
    assert summary["read_only"] is True
    assert summary["operator_review_required"] is True
    assert summary["manual_configuration_only"] is True
    assert summary["automated_dify_app_creation_allowed"] is False
    assert summary["dify_api_write_allowed"] is False
    assert summary["real_execution_allowed"] is False
    assert summary["trade_action_enabled"] is False
