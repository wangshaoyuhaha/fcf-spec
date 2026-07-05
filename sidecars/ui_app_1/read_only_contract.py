"""UI-APP-D1 read-only UI sidecar contract."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


UI_APP_READ_ONLY_CONTRACT: dict[str, Any] = {
    "app_id": "UI-APP-1",
    "stage_id": "UI-APP-D1",
    "contract_version": "1.0",
    "layer_type": "sidecar_ui_view",
    "paper_only": True,
    "local_only": True,
    "read_only": True,
    "sidecar_only": True,
    "core_imports_allowed": False,
    "core_mutation_allowed": False,
    "p48_core_expansion_allowed": False,
    "operator_review_required": True,
    "operator_review_bypass_allowed": False,
    "network_connectors_allowed": False,
    "credential_storage_allowed": False,
    "private_secret_access_allowed": False,
    "real_account_access_allowed": False,
    "real_position_access_allowed": False,
    "real_execution_allowed": False,
    "action_buttons_allowed": False,
    "upstream_sidecars": (
        "DATA-APP-1",
        "STOCK-APP-1",
        "AI-CONTEXT-1",
    ),
    "allowed_inputs": (
        "clean_universe",
        "watchlist",
        "quarantine_summary",
        "ranked_watchlist",
        "score_breakdown",
        "reason_codes",
        "risk_flags",
        "explanation_report",
        "operator_review_summary",
        "workflow_handoff_payload",
    ),
    "allowed_outputs": (
        "local_read_only_view_model",
        "local_read_only_html_report",
        "local_read_only_text_report",
        "paper_operator_review_record",
    ),
    "required_panels": (
        "workflow_status_panel",
        "candidate_pool_panel",
        "ranked_watchlist_panel",
        "score_breakdown_panel",
        "reason_codes_panel",
        "risk_flags_panel",
        "explanation_report_panel",
        "operator_review_summary_panel",
    ),
    "required_handoff_fields": (
        "app_id",
        "stage_id",
        "contract_version",
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
        "upstream_sidecars",
        "allowed_inputs",
        "allowed_outputs",
        "required_panels",
    ),
    "forbidden_capabilities": (
        "trade_action_buttons",
        "broker_connector",
        "market_execution_connector",
        "credential_storage",
        "private_secret_access",
        "real_account_access",
        "real_position_access",
        "real_execution",
        "core_mutation",
        "operator_review_bypass",
    ),
}


def get_read_only_ui_contract() -> dict[str, Any]:
    """Return a defensive copy of the UI-APP-D1 contract."""

    return deepcopy(UI_APP_READ_ONLY_CONTRACT)


def validate_read_only_ui_contract(
    contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate the UI-APP-D1 safety boundary and required fields."""

    candidate: Mapping[str, Any] = contract or UI_APP_READ_ONLY_CONTRACT
    errors: list[str] = []

    required_fields = candidate.get("required_handoff_fields", ())
    for field in required_fields:
        if field not in candidate:
            errors.append(f"missing_required_field:{field}")

    must_be_true = (
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
    )
    for field in must_be_true:
        if candidate.get(field) is not True:
            errors.append(f"expected_true:{field}")

    must_be_false = (
        "core_imports_allowed",
        "core_mutation_allowed",
        "p48_core_expansion_allowed",
        "operator_review_bypass_allowed",
        "network_connectors_allowed",
        "credential_storage_allowed",
        "private_secret_access_allowed",
        "real_account_access_allowed",
        "real_position_access_allowed",
        "real_execution_allowed",
        "action_buttons_allowed",
    )
    for field in must_be_false:
        if candidate.get(field) is not False:
            errors.append(f"expected_false:{field}")

    expected_upstreams = {"DATA-APP-1", "STOCK-APP-1", "AI-CONTEXT-1"}
    actual_upstreams = set(candidate.get("upstream_sidecars", ()))
    if actual_upstreams != expected_upstreams:
        errors.append("upstream_sidecars_mismatch")

    return {
        "ok": not errors,
        "errors": errors,
        "app_id": candidate.get("app_id"),
        "stage_id": candidate.get("stage_id"),
        "read_only": candidate.get("read_only"),
        "operator_review_required": candidate.get("operator_review_required"),
    }
