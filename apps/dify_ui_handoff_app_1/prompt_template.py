"""DIFY-UI-HANDOFF-D4 prompt template.

Paper-only local Dify/Ollama prompt package for reading FCF artifacts.
This module does not create Dify apps, does not call Dify APIs, and does not
perform real-world trading actions.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping, Optional

from apps.dify_ui_handoff_app_1.contract import APP_ID
from apps.dify_ui_handoff_app_1.dify_contract import (
    REQUIRED_OUTPUT_SECTIONS,
    build_safe_blocked_response,
    get_dify_io_contract,
    validate_dify_input_payload,
)


STAGE_ID = "DIFY-UI-HANDOFF-D4"
PROMPT_VERSION = "1.0.0"


SYSTEM_PROMPT = """
You are the local FCF Dify/Ollama operator assistant.

Allowed role:
- Read local FCF paper-only artifacts.
- Explain local report content for human operator review.
- Preserve risk_flags and reason_codes.
- Prepare safe operator review notes.

Hard boundaries:
- paper-only
- local-only
- read-only
- sidecar-only
- operator review required
- no real trading
- no real execution
- no broker connection
- no exchange connection
- no API key request
- no wallet private key request
- no real account access
- no real position access
- no order creation
- no automatic approval
- no guaranteed profit
- no future return guarantee
- no risk flag downgrade
- no reason code deletion

You must respond in Chinese.

Every response must contain these sections:
scope_status
artifact_summary
risk_flags
reason_codes
operator_review_notes
blocked_actions
next_safe_step
paper_only_notice
""".strip()


SAFETY_PROMPT = """
Safety instruction:

If the operator asks for real-world action, credentials, execution, order
placement, broker connection, exchange connection, account access, wallet
private key access, position sizing, portfolio action, or guaranteed return,
block that part.

Do not provide operational trading instructions.
Do not convert paper artifacts into real trade advice.
Do not infer missing risk fields as safe.
Do not remove or downgrade risk_flags.
Do not remove or downgrade reason_codes.
Do not bypass operator review.
""".strip()


USER_PROMPT_TEMPLATE = """
operator_question:
{operator_question}

paper_only_ack:
{paper_only_ack}

review_context:
{review_context}

fcf_manifest_text:
{fcf_manifest_text}

fcf_report_text:
{fcf_report_text}

Required response sections:
scope_status
artifact_summary
risk_flags
reason_codes
operator_review_notes
blocked_actions
next_safe_step
paper_only_notice
""".strip()


def get_dify_system_prompt() -> str:
    """Return the D4 system prompt."""
    return SYSTEM_PROMPT


def get_dify_safety_prompt() -> str:
    """Return the D4 safety prompt."""
    return SAFETY_PROMPT


def build_dify_user_prompt(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Build a local Dify user prompt from an input payload."""
    validation = validate_dify_input_payload(payload)
    if not validation["valid"]:
        return {
            "valid": False,
            "blocked": True,
            "issues": list(validation["issues"]),
            "blocked_matches": list(validation.get("blocked_matches", [])),
            "safe_blocked_response": build_safe_blocked_response(
                reason="invalid or unsafe Dify input payload",
                operator_question=str(payload.get("operator_question", "")),
            ),
        }

    rendered = USER_PROMPT_TEMPLATE.format(
        operator_question=payload.get("operator_question", ""),
        paper_only_ack=payload.get("paper_only_ack"),
        review_context=payload.get("review_context", ""),
        fcf_manifest_text=payload.get("fcf_manifest_text", ""),
        fcf_report_text=payload.get("fcf_report_text", ""),
    )

    return {
        "valid": True,
        "blocked": False,
        "issues": [],
        "prompt": rendered,
    }


def build_dify_prompt_package(
    payload: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Build the D4 local Dify prompt package."""
    selected_payload: Mapping[str, Any] = payload or {
        "operator_question": "Summarize the local FCF report for operator review.",
        "fcf_report_text": "",
        "fcf_manifest_text": "",
        "review_context": "",
        "paper_only_ack": True,
    }

    io_contract = get_dify_io_contract()
    user_prompt = build_dify_user_prompt(selected_payload)

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "prompt_version": PROMPT_VERSION,
        "system_prompt": get_dify_system_prompt(),
        "safety_prompt": get_dify_safety_prompt(),
        "user_prompt": deepcopy(user_prompt),
        "io_contract_summary": {
            "input_field_count": len(io_contract["input"]["input_fields"]),
            "required_output_section_count": len(
                io_contract["output"]["required_output_sections"]
            ),
            "source_count": io_contract["source_manifest_summary"]["source_count"],
            "missing_source_count": io_contract["source_manifest_summary"][
                "missing_source_count"
            ],
        },
        "required_output_sections": list(REQUIRED_OUTPUT_SECTIONS),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "real_execution_allowed": False,
        "trade_action_enabled": False,
        "automated_dify_app_creation_allowed": False,
        "dify_api_write_allowed": False,
    }


def validate_dify_prompt_package(package: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate the D4 prompt package."""
    issues = []

    if package.get("app_id") != APP_ID:
        issues.append("app_id mismatch")
    if package.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")
    if not package.get("system_prompt"):
        issues.append("system_prompt is required")
    if not package.get("safety_prompt"):
        issues.append("safety_prompt is required")
    if not package.get("user_prompt"):
        issues.append("user_prompt is required")

    prompt_text = (
        str(package.get("system_prompt", ""))
        + "\n"
        + str(package.get("safety_prompt", ""))
        + "\n"
        + str(package.get("user_prompt", ""))
    ).lower()

    required_phrases = [
        "paper-only",
        "local-only",
        "read-only",
        "operator review required",
        "no real trading",
        "no real execution",
        "risk_flags",
        "reason_codes",
    ]

    for phrase in required_phrases:
        if phrase not in prompt_text:
            issues.append("missing prompt phrase: " + phrase)

    for section in REQUIRED_OUTPUT_SECTIONS:
        if section not in package.get("required_output_sections", []):
            issues.append("missing required output section: " + section)

    required_true_fields = [
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
    ]

    required_false_fields = [
        "real_execution_allowed",
        "trade_action_enabled",
        "automated_dify_app_creation_allowed",
        "dify_api_write_allowed",
    ]

    for field in required_true_fields:
        if package.get(field) is not True:
            issues.append(field + " must be true")

    for field in required_false_fields:
        if package.get(field) is not False:
            issues.append(field + " must be false")

    summary = package.get("io_contract_summary", {})
    if summary.get("missing_source_count") != 0:
        issues.append("missing_source_count must be zero")

    return {
        "valid": not issues,
        "issues": issues,
        "stage_id": package.get("stage_id"),
        "prompt_version": package.get("prompt_version"),
        "blocked": bool(package.get("user_prompt", {}).get("blocked")),
    }


def summarize_dify_prompt_package(
    package: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Return compact D4 prompt package summary."""
    selected = dict(package) if package is not None else build_dify_prompt_package()
    validation = validate_dify_prompt_package(selected)

    return {
        "app_id": selected.get("app_id"),
        "stage_id": selected.get("stage_id"),
        "valid": validation["valid"],
        "blocked": validation["blocked"],
        "prompt_version": selected.get("prompt_version"),
        "required_output_section_count": len(
            selected.get("required_output_sections", [])
        ),
        "source_count": selected.get("io_contract_summary", {}).get("source_count"),
        "missing_source_count": selected.get("io_contract_summary", {}).get(
            "missing_source_count"
        ),
        "paper_only": selected.get("paper_only"),
        "local_only": selected.get("local_only"),
        "read_only": selected.get("read_only"),
        "operator_review_required": selected.get("operator_review_required"),
        "real_execution_allowed": selected.get("real_execution_allowed"),
        "trade_action_enabled": selected.get("trade_action_enabled"),
    }
