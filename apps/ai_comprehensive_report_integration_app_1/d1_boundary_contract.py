"""D1 boundary contract for comprehensive report integration."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

APP_ID = "AI-COMPREHENSIVE-REPORT-INTEGRATION-APP-1"
CONTRACT_VERSION = "1.0.0"
SOURCE_APP_ID = "AI-COMPREHENSIVE-REPORT-SYNTHESIS-APP-1"
SOURCE_ARTIFACT_TYPE = "comprehensive_report_synthesis_packet"

ALLOWED_CONSUMERS = (
    "OPERATOR-REVIEW-APP-1",
    "UI-APP-1",
    "REPORT-ARCHIVE-APP-1",
)

ALLOWED_OPERATIONS = (
    "load_registered_source",
    "validate_source_identity",
    "validate_source_version_lock",
    "validate_preservation_fields",
    "project_operator_review_packet",
    "project_ui_visibility_packet",
    "project_manual_archive_packet",
)

REQUIRED_PRESERVATION_FIELDS = (
    "correlation_id",
    "source_artifact_ref",
    "source_artifact_version",
    "source_statements",
    "original_conclusions",
    "risk_flags",
    "counterevidence",
    "alternative_explanations",
    "uncertainty_states",
    "operator_review_required",
)

FORBIDDEN_OPERATIONS = (
    "mutate_source_artifact",
    "overwrite_source_statement",
    "replace_original_conclusion",
    "invent_claim",
    "invent_evidence",
    "assign_probability",
    "select_winner",
    "auto_approve",
    "bypass_operator_review",
    "execute_archive",
    "invoke_live_model",
    "execute_prompt",
    "route_runtime",
    "switch_model_automatically",
    "switch_role_automatically",
    "place_order",
    "connect_broker_or_exchange",
    "read_real_account",
    "read_real_position",
    "create_tag",
    "create_release",
    "deploy",
)

SAFETY_BOUNDARY = {
    "core_frozen": True,
    "p48_allowed": False,
    "core_mutation_allowed": False,
    "paper_only": True,
    "local_only": True,
    "read_only": True,
    "sidecar_only": True,
    "registered_artifacts_only": True,
    "deterministic_only": True,
    "operator_review_required": True,
    "automatic_approval_allowed": False,
    "automatic_archive_execution_allowed": False,
    "runtime_orchestration_allowed": False,
    "live_model_invocation_allowed": False,
    "prompt_execution_allowed": False,
    "real_execution_allowed": False,
    "tag_allowed": False,
    "release_allowed": False,
    "deploy_allowed": False,
}


def build_integration_boundary_contract() -> dict[str, Any]:
    """Return the deterministic D1 integration boundary contract."""

    return {
        "app_id": APP_ID,
        "contract_version": CONTRACT_VERSION,
        "stage": "D1",
        "mode": "READ_ONLY_INTEGRATION",
        "source_app_id": SOURCE_APP_ID,
        "source_artifact_type": SOURCE_ARTIFACT_TYPE,
        "allowed_consumers": list(ALLOWED_CONSUMERS),
        "allowed_operations": list(ALLOWED_OPERATIONS),
        "required_preservation_fields": list(REQUIRED_PRESERVATION_FIELDS),
        "forbidden_operations": list(FORBIDDEN_OPERATIONS),
        "interpretation_state": {
            "causal_truth": "UNDETERMINED",
            "probability": "NOT_ASSIGNED",
            "winner": "NOT_SELECTED",
            "operator_decision": "PENDING",
            "archive_execution": "NOT_PERFORMED",
        },
        "safety_boundary": deepcopy(SAFETY_BOUNDARY),
    }


def validate_integration_boundary_contract(
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate required D1 fields without mutating the supplied contract."""

    errors: list[str] = []

    if contract.get("app_id") != APP_ID:
        errors.append("INVALID_APP_ID")

    if contract.get("contract_version") != CONTRACT_VERSION:
        errors.append("INVALID_CONTRACT_VERSION")

    if contract.get("stage") != "D1":
        errors.append("INVALID_STAGE")

    if contract.get("mode") != "READ_ONLY_INTEGRATION":
        errors.append("INVALID_MODE")

    if contract.get("source_app_id") != SOURCE_APP_ID:
        errors.append("INVALID_SOURCE_APP_ID")

    if contract.get("source_artifact_type") != SOURCE_ARTIFACT_TYPE:
        errors.append("INVALID_SOURCE_ARTIFACT_TYPE")

    if tuple(contract.get("allowed_consumers", ())) != ALLOWED_CONSUMERS:
        errors.append("INVALID_ALLOWED_CONSUMERS")

    if tuple(contract.get("allowed_operations", ())) != ALLOWED_OPERATIONS:
        errors.append("INVALID_ALLOWED_OPERATIONS")

    if tuple(
        contract.get("required_preservation_fields", ())
    ) != REQUIRED_PRESERVATION_FIELDS:
        errors.append("INVALID_PRESERVATION_FIELDS")

    if tuple(contract.get("forbidden_operations", ())) != FORBIDDEN_OPERATIONS:
        errors.append("INVALID_FORBIDDEN_OPERATIONS")

    interpretation_state = contract.get("interpretation_state")

    if not isinstance(interpretation_state, Mapping):
        errors.append("INVALID_INTERPRETATION_STATE")
    else:
        expected_interpretation = {
            "causal_truth": "UNDETERMINED",
            "probability": "NOT_ASSIGNED",
            "winner": "NOT_SELECTED",
            "operator_decision": "PENDING",
            "archive_execution": "NOT_PERFORMED",
        }

        if dict(interpretation_state) != expected_interpretation:
            errors.append("UNSAFE_INTERPRETATION_STATE")

    safety_boundary = contract.get("safety_boundary")

    if not isinstance(safety_boundary, Mapping):
        errors.append("INVALID_SAFETY_BOUNDARY")
    else:
        for field, required_value in SAFETY_BOUNDARY.items():
            if safety_boundary.get(field) is not required_value:
                errors.append(f"UNSAFE_BOUNDARY_{field.upper()}")

    return {
        "app_id": APP_ID,
        "contract_version": CONTRACT_VERSION,
        "ok": not errors,
        "errors": sorted(set(errors)),
        "operator_review_required": True,
        "source_mutation_performed": False,
        "archive_execution_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }
