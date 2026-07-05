"""UI-APP-D6 final workflow handoff and closeout."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


UI_APP_D6_FINAL_HANDOFF: dict[str, Any] = {
    "app_id": "UI-APP-1",
    "stage_id": "UI-APP-D6",
    "status": "CLOSED_OUT",
    "paper_only": True,
    "local_only": True,
    "read_only": True,
    "sidecar_only": True,
    "operator_review_required": True,
    "operator_review_bypass_allowed": False,
    "core_mutation_allowed": False,
    "p48_core_expansion_allowed": False,
    "trade_action_enabled": False,
    "buy_button_enabled": False,
    "sell_button_enabled": False,
    "order_button_enabled": False,
    "broker_connection_allowed": False,
    "exchange_connection_allowed": False,
    "credential_storage_allowed": False,
    "wallet_private_key_access_allowed": False,
    "real_account_access_allowed": False,
    "real_position_access_allowed": False,
    "real_execution_allowed": False,
    "completed_steps": (
        "UI-APP-D1 read-only UI contract",
        "UI-APP-D2 AI-CONTEXT handoff loader",
        "UI-APP-D3 ranked watchlist view model",
        "UI-APP-D4 risk reason review panels",
        "UI-APP-D5 local report artifact",
        "UI-APP-D6 final workflow handoff closeout",
    ),
    "upstream_sidecars": (
        "DATA-APP-1",
        "STOCK-APP-1",
        "AI-CONTEXT-1",
    ),
    "handoff_to_main_window_required": True,
    "next_phase_source_file_required": True,
    "tag_allowed": False,
    "release_allowed": False,
    "deploy_allowed": False,
}


def get_ui_app_d6_final_handoff() -> dict[str, Any]:
    """Return a defensive copy of the final UI-APP-1 handoff."""

    return deepcopy(UI_APP_D6_FINAL_HANDOFF)


def validate_ui_app_d6_final_handoff(
    handoff: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate final UI-APP-1 closeout safety."""

    candidate = handoff or UI_APP_D6_FINAL_HANDOFF
    errors: list[str] = []

    must_be_true = (
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
        "handoff_to_main_window_required",
        "next_phase_source_file_required",
    )
    for field in must_be_true:
        if candidate.get(field) is not True:
            errors.append(f"expected_true:{field}")

    must_be_false = (
        "operator_review_bypass_allowed",
        "core_mutation_allowed",
        "p48_core_expansion_allowed",
        "trade_action_enabled",
        "buy_button_enabled",
        "sell_button_enabled",
        "order_button_enabled",
        "broker_connection_allowed",
        "exchange_connection_allowed",
        "credential_storage_allowed",
        "wallet_private_key_access_allowed",
        "real_account_access_allowed",
        "real_position_access_allowed",
        "real_execution_allowed",
        "tag_allowed",
        "release_allowed",
        "deploy_allowed",
    )
    for field in must_be_false:
        if candidate.get(field) is not False:
            errors.append(f"expected_false:{field}")

    completed_steps = candidate.get("completed_steps", ())
    if len(completed_steps) != 6:
        errors.append("completed_steps_count_mismatch")

    expected_upstreams = {"DATA-APP-1", "STOCK-APP-1", "AI-CONTEXT-1"}
    if set(candidate.get("upstream_sidecars", ())) != expected_upstreams:
        errors.append("upstream_sidecars_mismatch")

    return {
        "ok": not errors,
        "errors": errors,
        "app_id": candidate.get("app_id"),
        "stage_id": candidate.get("stage_id"),
        "status": candidate.get("status"),
    }
