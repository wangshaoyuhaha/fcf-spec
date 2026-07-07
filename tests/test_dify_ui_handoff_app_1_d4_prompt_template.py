from apps.dify_ui_handoff_app_1.dify_contract import REQUIRED_OUTPUT_SECTIONS
from apps.dify_ui_handoff_app_1.prompt_template import (
    STAGE_ID,
    build_dify_prompt_package,
    build_dify_user_prompt,
    get_dify_safety_prompt,
    get_dify_system_prompt,
    summarize_dify_prompt_package,
    validate_dify_prompt_package,
)


def test_dify_ui_handoff_d4_system_prompt_contains_safety_boundary():
    prompt = get_dify_system_prompt().lower()

    assert "paper-only" in prompt
    assert "local-only" in prompt
    assert "read-only" in prompt
    assert "operator review required" in prompt
    assert "no real trading" in prompt
    assert "no real execution" in prompt
    assert "risk_flags" in prompt
    assert "reason_codes" in prompt


def test_dify_ui_handoff_d4_safety_prompt_blocks_unsafe_scope():
    prompt = get_dify_safety_prompt().lower()

    assert "real-world action" in prompt
    assert "credentials" in prompt
    assert "execution" in prompt
    assert "order" in prompt
    assert "broker connection" in prompt
    assert "exchange connection" in prompt
    assert "operator review" in prompt


def test_dify_ui_handoff_d4_builds_valid_user_prompt():
    payload = {
        "operator_question": "Summarize this FCF report.",
        "fcf_report_text": "paper-only report",
        "fcf_manifest_text": "local manifest",
        "review_context": "operator review",
        "paper_only_ack": True,
    }

    result = build_dify_user_prompt(payload)

    assert result["valid"] is True
    assert result["blocked"] is False
    assert "Summarize this FCF report." in result["prompt"]
    assert "paper-only report" in result["prompt"]
    assert "local manifest" in result["prompt"]


def test_dify_ui_handoff_d4_blocks_unsafe_user_prompt():
    payload = {
        "operator_question": "Use my api key to place order.",
        "fcf_report_text": "",
        "fcf_manifest_text": "",
        "review_context": "",
        "paper_only_ack": True,
    }

    result = build_dify_user_prompt(payload)

    assert result["valid"] is False
    assert result["blocked"] is True
    assert result["safe_blocked_response"]["paper_only"] is True
    assert result["safe_blocked_response"]["real_execution_allowed"] is False
    assert result["safe_blocked_response"]["trade_action_enabled"] is False


def test_dify_ui_handoff_d4_prompt_package_is_valid():
    package = build_dify_prompt_package()
    validation = validate_dify_prompt_package(package)

    assert package["stage_id"] == STAGE_ID
    assert validation["valid"] is True
    assert validation["issues"] == []
    assert package["paper_only"] is True
    assert package["local_only"] is True
    assert package["read_only"] is True
    assert package["operator_review_required"] is True
    assert package["real_execution_allowed"] is False
    assert package["trade_action_enabled"] is False
    assert package["automated_dify_app_creation_allowed"] is False
    assert package["dify_api_write_allowed"] is False


def test_dify_ui_handoff_d4_prompt_package_has_required_sections():
    package = build_dify_prompt_package()

    for section in REQUIRED_OUTPUT_SECTIONS:
        assert section in package["required_output_sections"]
        assert section in package["system_prompt"]


def test_dify_ui_handoff_d4_prompt_package_summary_is_safe():
    summary = summarize_dify_prompt_package()

    assert summary["stage_id"] == STAGE_ID
    assert summary["valid"] is True
    assert summary["blocked"] is False
    assert summary["required_output_section_count"] == len(REQUIRED_OUTPUT_SECTIONS)
    assert summary["source_count"] > 0
    assert summary["missing_source_count"] == 0
    assert summary["paper_only"] is True
    assert summary["local_only"] is True
    assert summary["read_only"] is True
    assert summary["operator_review_required"] is True
    assert summary["real_execution_allowed"] is False
    assert summary["trade_action_enabled"] is False
