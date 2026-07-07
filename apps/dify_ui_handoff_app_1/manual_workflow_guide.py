"""DIFY-UI-HANDOFF-D5 manual workflow guide.

This module defines a repo-stored manual Dify configuration guide.
It does not deploy Dify, does not call Dify APIs, and does not create apps.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Mapping, Optional

from apps.dify_ui_handoff_app_1.contract import APP_ID
from apps.dify_ui_handoff_app_1.dify_contract import REQUIRED_OUTPUT_SECTIONS
from apps.dify_ui_handoff_app_1.prompt_template import build_dify_prompt_package


STAGE_ID = "DIFY-UI-HANDOFF-D5"
GUIDE_VERSION = "1.0.0"

REQUIRED_VARIABLES: List[Dict[str, Any]] = [
    {"name": "operator_question", "type": "text", "required": True},
    {"name": "fcf_report_text", "type": "paragraph", "required": False},
    {"name": "fcf_manifest_text", "type": "paragraph", "required": False},
    {"name": "review_context", "type": "text", "required": False},
    {"name": "paper_only_ack", "type": "boolean", "required": True},
]

MANUAL_WORKFLOW_STEPS: List[Dict[str, Any]] = [
    {
        "step_id": "D5-S1",
        "title": "Create local manual Dify app",
        "operator_action": "Create a manual chatflow or workflow app in local Dify.",
        "required_setting": "No external tool, no plugin, no API write.",
    },
    {
        "step_id": "D5-S2",
        "title": "Add input variables",
        "operator_action": "Create variables listed in REQUIRED_VARIABLES.",
        "required_setting": "paper_only_ack must be required and true.",
    },
    {
        "step_id": "D5-S3",
        "title": "Paste system and safety prompts",
        "operator_action": "Paste D4 system_prompt and safety_prompt into the LLM node.",
        "required_setting": "Do not remove safety boundary text.",
    },
    {
        "step_id": "D5-S4",
        "title": "Use local report text only",
        "operator_action": "Paste local FCF report or manifest text into input fields.",
        "required_setting": "No broker, exchange, wallet, credential, or real account connection.",
    },
    {
        "step_id": "D5-S5",
        "title": "Require structured safe response",
        "operator_action": "Require all D3 output sections in the answer.",
        "required_setting": "risk_flags and reason_codes must be visible.",
    },
    {
        "step_id": "D5-S6",
        "title": "Operator review before any next step",
        "operator_action": "Review output manually before using it as paper-only interpretation.",
        "required_setting": "No automatic approval and no real-world execution.",
    },
]

BLOCKED_CONFIGURATION_ITEMS: List[str] = [
    "dify_api_write",
    "automatic_app_creation",
    "external_tool_call",
    "broker_connection",
    "exchange_connection",
    "api_key_variable",
    "wallet_private_key_variable",
    "real_account_variable",
    "real_position_variable",
    "order_execution_node",
    "trade_action_button",
    "operator_review_bypass",
]

REQUIRED_SAFETY_SETTINGS: Dict[str, Any] = {
    "paper_only": True,
    "local_only": True,
    "read_only": True,
    "sidecar_only": True,
    "operator_review_required": True,
    "manual_configuration_only": True,
    "automated_dify_app_creation_allowed": False,
    "dify_api_write_allowed": False,
    "real_execution_allowed": False,
    "trade_action_enabled": False,
}


def build_dify_manual_workflow_guide() -> Dict[str, Any]:
    """Build the D5 manual Dify workflow guide."""
    prompt_package = build_dify_prompt_package()

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "guide_version": GUIDE_VERSION,
        "purpose": "Manual local Dify configuration guide for FCF paper-only report reading.",
        "required_variables": deepcopy(REQUIRED_VARIABLES),
        "manual_workflow_steps": deepcopy(MANUAL_WORKFLOW_STEPS),
        "blocked_configuration_items": list(BLOCKED_CONFIGURATION_ITEMS),
        "required_output_sections": list(REQUIRED_OUTPUT_SECTIONS),
        "prompt_package_summary": {
            "stage_id": prompt_package["stage_id"],
            "prompt_version": prompt_package["prompt_version"],
            "required_output_section_count": len(prompt_package["required_output_sections"]),
            "missing_source_count": prompt_package["io_contract_summary"]["missing_source_count"],
        },
        "safety_settings": deepcopy(REQUIRED_SAFETY_SETTINGS),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "manual_configuration_only": True,
        "automated_dify_app_creation_allowed": False,
        "dify_api_write_allowed": False,
        "real_execution_allowed": False,
        "trade_action_enabled": False,
    }


def validate_dify_manual_workflow_guide(
    guide: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Validate the D5 manual Dify workflow guide."""
    selected = dict(guide) if guide is not None else build_dify_manual_workflow_guide()
    issues: List[str] = []

    if selected.get("app_id") != APP_ID:
        issues.append("app_id mismatch")
    if selected.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

    if not selected.get("required_variables"):
        issues.append("required_variables must not be empty")
    if not selected.get("manual_workflow_steps"):
        issues.append("manual_workflow_steps must not be empty")

    variable_names = {
        item.get("name")
        for item in selected.get("required_variables", [])
    }
    for required_name in [
        "operator_question",
        "fcf_report_text",
        "fcf_manifest_text",
        "review_context",
        "paper_only_ack",
    ]:
        if required_name not in variable_names:
            issues.append("missing required variable: " + required_name)

    for section in REQUIRED_OUTPUT_SECTIONS:
        if section not in selected.get("required_output_sections", []):
            issues.append("missing required output section: " + section)

    for blocked_item in BLOCKED_CONFIGURATION_ITEMS:
        if blocked_item not in selected.get("blocked_configuration_items", []):
            issues.append("missing blocked configuration item: " + blocked_item)

    safety_settings = selected.get("safety_settings", {})
    for field, expected in REQUIRED_SAFETY_SETTINGS.items():
        if safety_settings.get(field) is not expected:
            issues.append("safety setting mismatch: " + field)

    for field in [
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
        "manual_configuration_only",
    ]:
        if selected.get(field) is not True:
            issues.append(field + " must be true")

    for field in [
        "automated_dify_app_creation_allowed",
        "dify_api_write_allowed",
        "real_execution_allowed",
        "trade_action_enabled",
    ]:
        if selected.get(field) is not False:
            issues.append(field + " must be false")

    return {
        "valid": not issues,
        "issues": issues,
        "stage_id": selected.get("stage_id"),
        "guide_version": selected.get("guide_version"),
        "required_variable_count": len(selected.get("required_variables", [])),
        "workflow_step_count": len(selected.get("manual_workflow_steps", [])),
        "blocked_configuration_count": len(
            selected.get("blocked_configuration_items", [])
        ),
    }


def summarize_dify_manual_workflow_guide(
    guide: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Return a compact D5 guide summary."""
    selected = dict(guide) if guide is not None else build_dify_manual_workflow_guide()
    validation = validate_dify_manual_workflow_guide(selected)

    return {
        "app_id": selected.get("app_id"),
        "stage_id": selected.get("stage_id"),
        "valid": validation["valid"],
        "guide_version": selected.get("guide_version"),
        "required_variable_count": validation["required_variable_count"],
        "workflow_step_count": validation["workflow_step_count"],
        "blocked_configuration_count": validation["blocked_configuration_count"],
        "paper_only": selected.get("paper_only"),
        "local_only": selected.get("local_only"),
        "read_only": selected.get("read_only"),
        "operator_review_required": selected.get("operator_review_required"),
        "manual_configuration_only": selected.get("manual_configuration_only"),
        "automated_dify_app_creation_allowed": selected.get(
            "automated_dify_app_creation_allowed"
        ),
        "dify_api_write_allowed": selected.get("dify_api_write_allowed"),
        "real_execution_allowed": selected.get("real_execution_allowed"),
        "trade_action_enabled": selected.get("trade_action_enabled"),
    }
