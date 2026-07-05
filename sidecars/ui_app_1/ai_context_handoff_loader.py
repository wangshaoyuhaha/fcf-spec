"""UI-APP-D2 AI-CONTEXT handoff payload loader.

This module only reads local JSON handoff payloads.
It does not mutate core state, call networks, or create execution actions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


AI_CONTEXT_HANDOFF_REQUIRED_FIELDS: tuple[str, ...] = (
    "app_id",
    "stage_id",
    "paper_only",
    "local_only",
    "read_only",
    "sidecar_only",
    "operator_review_required",
    "ranked_watchlist",
    "explanation_report",
    "operator_review_summary",
)


class UIAppHandoffLoadError(ValueError):
    """Raised when a local AI-CONTEXT handoff payload is invalid."""


def load_ai_context_handoff_payload(path: str | Path) -> dict[str, Any]:
    """Load a local AI-CONTEXT handoff payload from JSON."""

    payload_path = Path(path)
    if not payload_path.exists():
        raise UIAppHandoffLoadError(f"handoff_payload_not_found:{payload_path}")

    if payload_path.suffix.lower() != ".json":
        raise UIAppHandoffLoadError("handoff_payload_must_be_json")

    try:
        data = json.loads(payload_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise UIAppHandoffLoadError("handoff_payload_invalid_json") from exc

    if not isinstance(data, dict):
        raise UIAppHandoffLoadError("handoff_payload_must_be_object")

    result = validate_ai_context_handoff_payload(data)
    if not result["ok"]:
        joined = ",".join(result["errors"])
        raise UIAppHandoffLoadError(f"handoff_payload_invalid:{joined}")

    return data


def validate_ai_context_handoff_payload(
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate that a payload is safe for the read-only UI layer."""

    errors: list[str] = []

    for field in AI_CONTEXT_HANDOFF_REQUIRED_FIELDS:
        if field not in payload:
            errors.append(f"missing_required_field:{field}")

    must_be_true = (
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
    )
    for field in must_be_true:
        if payload.get(field) is not True:
            errors.append(f"expected_true:{field}")

    forbidden_truthy_fields = (
        "trade_action_allowed",
        "buy_button_allowed",
        "sell_button_allowed",
        "order_button_allowed",
        "broker_connection_allowed",
        "exchange_connection_allowed",
        "credential_storage_allowed",
        "wallet_private_key_access_allowed",
        "real_account_access_allowed",
        "real_position_access_allowed",
        "real_execution_allowed",
        "operator_review_bypass_allowed",
        "core_mutation_allowed",
    )
    for field in forbidden_truthy_fields:
        if payload.get(field) is True:
            errors.append(f"forbidden_true:{field}")

    if not isinstance(payload.get("ranked_watchlist", []), list):
        errors.append("ranked_watchlist_must_be_list")

    if not isinstance(payload.get("explanation_report", {}), Mapping):
        errors.append("explanation_report_must_be_object")

    if not isinstance(payload.get("operator_review_summary", {}), Mapping):
        errors.append("operator_review_summary_must_be_object")

    return {
        "ok": not errors,
        "errors": errors,
        "app_id": payload.get("app_id"),
        "stage_id": payload.get("stage_id"),
        "candidate_count": len(payload.get("ranked_watchlist", []))
        if isinstance(payload.get("ranked_watchlist", []), list)
        else None,
        "operator_review_required": payload.get("operator_review_required"),
    }


def summarize_ai_context_handoff_payload(
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    """Return a compact read-only summary for UI workflow routing."""

    validation = validate_ai_context_handoff_payload(payload)
    if not validation["ok"]:
        return {
            "ok": False,
            "errors": validation["errors"],
            "candidate_count": None,
            "panel_ready": False,
        }

    explanation_report = payload.get("explanation_report", {})
    operator_review_summary = payload.get("operator_review_summary", {})

    return {
        "ok": True,
        "errors": [],
        "candidate_count": validation["candidate_count"],
        "panel_ready": True,
        "app_id": payload.get("app_id"),
        "stage_id": payload.get("stage_id"),
        "explanation_report_keys": sorted(explanation_report.keys()),
        "operator_review_summary_keys": sorted(operator_review_summary.keys()),
        "operator_review_required": payload.get("operator_review_required"),
    }
