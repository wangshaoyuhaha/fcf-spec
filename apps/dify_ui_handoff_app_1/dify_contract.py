"""DIFY-UI-HANDOFF-D3 Dify input and output contract.

This module defines the safe local Dify app contract for FCF report reading.
It is paper-only, local-only, read-only, and operator-review-required.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Mapping, Optional

from apps.dify_ui_handoff_app_1.contract import APP_ID, FORBIDDEN_DIFY_OUTPUTS, SAFETY_FLAGS
from apps.dify_ui_handoff_app_1.source_loader import build_dify_ui_source_manifest


STAGE_ID = "DIFY-UI-HANDOFF-D3"
CONTRACT_VERSION = "1.0.0"

DIFY_APP_MODE = "local_manual_chatflow_or_workflow"
DIFY_PURPOSE = (
    "Read local FCF reports and explain paper-only research outputs for human "
    "operator review. The Dify app must not create trade instructions, orders, "
    "position sizing, execution actions, or real-world financial advice."
)

INPUT_FIELDS: List[Dict[str, Any]] = [
    {
        "name": "operator_question",
        "type": "text",
        "required": True,
        "description": "Human operator question about local FCF artifacts.",
    },
    {
        "name": "fcf_report_text",
        "type": "long_text",
        "required": False,
        "description": "Optional pasted content from a local FCF report.",
    },
    {
        "name": "fcf_manifest_text",
        "type": "long_text",
        "required": False,
        "description": "Optional pasted content from UI, workflow, or source manifest.",
    },
    {
        "name": "review_context",
        "type": "text",
        "required": False,
        "description": "Optional operator review context or review question.",
    },
    {
        "name": "paper_only_ack",
        "type": "boolean",
        "required": True,
        "description": "Must be true. Confirms the operator understands this is paper-only.",
    },
]

REQUIRED_OUTPUT_SECTIONS: List[str] = [
    "scope_status",
    "artifact_summary",
    "risk_flags",
    "reason_codes",
    "operator_review_notes",
    "blocked_actions",
    "next_safe_step",
    "paper_only_notice",
]

OUTPUT_CONTRACT: Dict[str, Any] = {
    "response_language": "Chinese",
    "must_include_sections": list(REQUIRED_OUTPUT_SECTIONS),
    "must_preserve": [
        "risk_flags",
        "reason_codes",
        "operator_review_required",
        "paper_only",
        "local_only",
        "read_only",
        "no_real_execution",
    ],
    "must_not_generate": list(FORBIDDEN_DIFY_OUTPUTS),
    "must_not_claim": [
        "real trade success",
        "real order placed",
        "exchange rejection",
        "broker rejection",
        "guaranteed profit",
        "guaranteed return",
        "future return certainty",
    ],
    "allowed_actions": [
        "summarize local report",
        "explain risk flags",
        "explain reason codes",
        "identify missing review fields",
        "prepare human review notes",
        "explain why an action is blocked",
        "suggest next safe paper-only review step",
    ],
    "blocked_actions": [
        "buy",
        "sell",
        "place order",
        "cancel order",
        "connect exchange",
        "connect broker",
        "request api key",
        "request wallet private key",
        "read real account balance",
        "read real position",
        "size real position",
        "rebalance real portfolio",
        "bypass operator review",
    ],
}

DIFY_VARIABLE_TEMPLATE: Dict[str, Any] = {
    "operator_question": "",
    "fcf_report_text": "",
    "fcf_manifest_text": "",
    "review_context": "",
    "paper_only_ack": True,
}

SAFETY_ACK_REQUIREMENTS: Dict[str, Any] = {
    "paper_only_ack_must_be_true": True,
    "empty_operator_question_allowed": False,
    "real_trading_request_must_be_blocked": True,
    "api_key_request_must_be_blocked": True,
    "wallet_private_key_request_must_be_blocked": True,
    "operator_review_required": True,
}


def get_dify_input_contract() -> Dict[str, Any]:
    """Return the D3 Dify input contract."""
    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "app_mode": DIFY_APP_MODE,
        "purpose": DIFY_PURPOSE,
        "input_fields": deepcopy(INPUT_FIELDS),
        "variable_template": deepcopy(DIFY_VARIABLE_TEMPLATE),
        "safety_ack_requirements": deepcopy(SAFETY_ACK_REQUIREMENTS),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "manual_dify_configuration_required": True,
        "automated_dify_app_creation_allowed": False,
        "dify_api_write_allowed": False,
    }


def get_dify_output_contract() -> Dict[str, Any]:
    """Return the D3 Dify output contract."""
    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "output_contract": deepcopy(OUTPUT_CONTRACT),
        "required_output_sections": list(REQUIRED_OUTPUT_SECTIONS),
        "safety_flags": deepcopy(SAFETY_FLAGS),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "real_execution_allowed": False,
        "trade_action_enabled": False,
        "buy_button_enabled": False,
        "sell_button_enabled": False,
        "order_button_enabled": False,
        "operator_review_bypass_allowed": False,
        "risk_flag_downgrade_allowed": False,
        "reason_code_mutation_allowed": False,
    }


def get_dify_io_contract() -> Dict[str, Any]:
    """Return combined D3 input/output contract."""
    source_manifest = build_dify_ui_source_manifest()
    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "input": get_dify_input_contract(),
        "output": get_dify_output_contract(),
        "source_manifest_summary": {
            "source_count": source_manifest["source_count"],
            "existing_source_count": source_manifest["existing_source_count"],
            "missing_source_count": source_manifest["missing_source_count"],
            "child_file_count": source_manifest["child_file_count"],
        },
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
    }


def validate_dify_input_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate one local Dify input payload before prompt use."""
    issues: List[str] = []

    if not isinstance(payload.get("operator_question"), str) or not payload.get("operator_question", "").strip():
        issues.append("operator_question is required")

    if payload.get("paper_only_ack") is not True:
        issues.append("paper_only_ack must be true")

    for optional_text_field in ["fcf_report_text", "fcf_manifest_text", "review_context"]:
        value = payload.get(optional_text_field, "")
        if value is not None and not isinstance(value, str):
            issues.append(optional_text_field + " must be text")

    lower_text = " ".join(
        str(payload.get(field, ""))
        for field in ["operator_question", "fcf_report_text", "fcf_manifest_text", "review_context"]
    ).lower()

    blocked_terms = [
        "api key",
        "private key",
        "wallet key",
        "real order",
        "place order",
        "buy now",
        "sell now",
        "execute trade",
        "connect broker",
        "connect exchange",
        "real account",
        "real position",
    ]

    blocked_matches = [term for term in blocked_terms if term in lower_text]
    if blocked_matches:
        issues.append("blocked real-world request terms detected: " + ", ".join(blocked_matches))

    return {
        "valid": not issues,
        "issues": issues,
        "paper_only_ack": payload.get("paper_only_ack"),
        "blocked": bool(blocked_matches) if "blocked_matches" in locals() else False,
        "blocked_matches": blocked_matches if "blocked_matches" in locals() else [],
    }


def validate_dify_output_response(response: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate a structured Dify response against the output contract."""
    issues: List[str] = []

    sections = response.get("sections", {})
    if not isinstance(sections, Mapping):
        issues.append("sections must be a mapping")
        sections = {}

    for section in REQUIRED_OUTPUT_SECTIONS:
        if section not in sections:
            issues.append("missing output section: " + section)

    if response.get("paper_only") is not True:
        issues.append("paper_only must be true")
    if response.get("operator_review_required") is not True:
        issues.append("operator_review_required must be true")
    if response.get("real_execution_allowed") is not False:
        issues.append("real_execution_allowed must be false")
    if response.get("trade_action_enabled") is not False:
        issues.append("trade_action_enabled must be false")

    response_text = str(response).lower()
    forbidden_hits = [
        phrase
        for phrase in ["buy now", "sell now", "place order", "execute trade", "guaranteed profit"]
        if phrase in response_text
    ]
    if forbidden_hits:
        issues.append("forbidden output terms detected: " + ", ".join(forbidden_hits))

    return {
        "valid": not issues,
        "issues": issues,
        "forbidden_hits": forbidden_hits,
        "required_section_count": len(REQUIRED_OUTPUT_SECTIONS),
        "present_section_count": len(sections),
    }


def build_safe_blocked_response(reason: str, operator_question: str = "") -> Dict[str, Any]:
    """Build a safe blocked response for Dify real-world or unsafe requests."""
    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "operator_review_required": True,
        "real_execution_allowed": False,
        "trade_action_enabled": False,
        "status": "BLOCKED_UNSAFE_OR_REAL_WORLD_REQUEST",
        "operator_question": "[redacted unsafe operator question]",
        "operator_question_redacted": True,
        "reason": reason,
        "sections": {
            "scope_status": "Blocked. This workflow is paper-only and local-only.",
            "artifact_summary": "No artifact was changed. No real-world action was taken.",
            "risk_flags": ["REAL_WORLD_ACTION_REQUEST_BLOCKED"],
            "reason_codes": ["DIFY_OUTPUT_SAFETY_BLOCK"],
            "operator_review_notes": "Human operator review is required before any future paper-only interpretation.",
            "blocked_actions": [
                "real_world_action_blocked",
                "credential_request_blocked",
                "execution_request_blocked",
                "operator_review_bypass_blocked",
            ],
            "next_safe_step": "Use only local FCF reports and ask for paper-only explanation.",
            "paper_only_notice": "No real trading, no real execution, no API keys, no broker or exchange connection.",
        },
    }


def summarize_dify_io_contract(contract: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """Return compact D3 summary."""
    selected = dict(contract) if contract is not None else get_dify_io_contract()
    output = selected["output"]
    return {
        "app_id": selected.get("app_id"),
        "stage_id": selected.get("stage_id"),
        "input_field_count": len(selected["input"]["input_fields"]),
        "required_output_section_count": len(output["required_output_sections"]),
        "source_count": selected["source_manifest_summary"]["source_count"],
        "missing_source_count": selected["source_manifest_summary"]["missing_source_count"],
        "paper_only": selected.get("paper_only"),
        "local_only": selected.get("local_only"),
        "read_only": selected.get("read_only"),
        "operator_review_required": selected.get("operator_review_required"),
        "real_execution_allowed": output.get("real_execution_allowed"),
        "trade_action_enabled": output.get("trade_action_enabled"),
    }
