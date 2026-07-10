"""Boundary contract for deterministic AI evaluation drift review."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


APP_ID = "AI-EVALUATION-DRIFT-REVIEW-APP-1"
STAGE_ID = "D1_BOUNDARY_CONTRACT"
CONTRACT_VERSION = "1.0.0"

ALLOWED_INPUTS = (
    "registered_comparison_record",
    "registered_comparison_matrix",
    "comparison_review_packet",
    "comparison_operator_handoff",
    "evaluation_time_metadata",
    "model_version_metadata",
    "prompt_version_metadata",
)

ALLOWED_OUTPUTS = (
    "drift_evidence_record",
    "drift_classification_report",
    "drift_window_report",
    "drift_review_packet",
    "drift_operator_handoff",
)

REQUIRED_DRIFT_DIMENSIONS = (
    "evaluation_sample_id",
    "baseline_reference",
    "candidate_reference",
    "baseline_created_at_utc",
    "candidate_created_at_utc",
    "model_id",
    "model_version",
    "prompt_id",
    "prompt_version",
)

DRIFT_STATUSES = (
    "NO_DRIFT",
    "POTENTIAL_DRIFT",
    "CONFIRMED_DRIFT",
    "INSUFFICIENT_EVIDENCE",
    "REVIEW_REQUIRED",
    "INVALID",
    "BLOCKED",
    "ARCHIVED",
)

FORBIDDEN_DRIFT_STATUSES = (
    "AUTO_APPROVED",
    "AUTO_REJECTED",
    "AUTO_ROLLED_BACK",
    "AUTO_MODEL_SWITCH",
    "AUTO_PROMPT_SWITCH",
    "TRADE_READY",
    "EXECUTION_READY",
    "LIVE_READY",
)

_REQUIRED_TRUE_FLAGS = (
    "paper_only",
    "local_only",
    "read_only",
    "sidecar_only",
    "operator_review_required",
    "deterministic_only",
    "registered_artifacts_only",
)

_REQUIRED_FALSE_FLAGS = (
    "core_mutation_allowed",
    "model_invocation_allowed",
    "prompt_execution_allowed",
    "orchestrator_execution_allowed",
    "automatic_approval_allowed",
    "automatic_rejection_allowed",
    "automatic_rollback_allowed",
    "automatic_model_switch_allowed",
    "automatic_prompt_switch_allowed",
    "trade_action_allowed",
    "real_execution_allowed",
)


def build_boundary_contract() -> dict[str, Any]:
    """Build the immutable Drift D1 boundary contract."""

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "allowed_inputs": list(ALLOWED_INPUTS),
        "allowed_outputs": list(ALLOWED_OUTPUTS),
        "required_drift_dimensions": list(
            REQUIRED_DRIFT_DIMENSIONS
        ),
        "drift_statuses": list(DRIFT_STATUSES),
        "forbidden_drift_statuses": list(
            FORBIDDEN_DRIFT_STATUSES
        ),
        "next_stage": "D2_DRIFT_EVIDENCE_SCHEMA",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "deterministic_only": True,
        "registered_artifacts_only": True,
        "core_mutation_allowed": False,
        "model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "orchestrator_execution_allowed": False,
        "automatic_approval_allowed": False,
        "automatic_rejection_allowed": False,
        "automatic_rollback_allowed": False,
        "automatic_model_switch_allowed": False,
        "automatic_prompt_switch_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
    }


def _validate_exact_string_list(
    *,
    field: str,
    value: Any,
    expected: tuple[str, ...],
) -> list[str]:
    if not isinstance(value, list):
        return [f"{field}_invalid"]

    errors: list[str] = []

    if any(
        not isinstance(item, str) or not item.strip()
        for item in value
    ):
        errors.append(f"{field}_invalid")
        return errors

    if len(value) != len(set(value)):
        errors.append(f"{field}_duplicate")

    missing = sorted(set(expected) - set(value))
    unexpected = sorted(set(value) - set(expected))

    for item in missing:
        errors.append(f"{field}_missing:{item}")

    for item in unexpected:
        errors.append(f"{field}_unexpected:{item}")

    if not missing and not unexpected and value != list(expected):
        errors.append(f"{field}_order_mismatch")

    return errors


def validate_boundary_contract(
    contract: Mapping[str, Any],
) -> list[str]:
    """Return deterministic boundary-contract validation errors."""

    if not isinstance(contract, Mapping):
        return ["contract_not_mapping"]

    errors: list[str] = []

    if contract.get("app_id") != APP_ID:
        errors.append("app_id_mismatch")

    if contract.get("stage_id") != STAGE_ID:
        errors.append("stage_id_mismatch")

    if contract.get("contract_version") != CONTRACT_VERSION:
        errors.append("contract_version_mismatch")

    errors.extend(
        _validate_exact_string_list(
            field="allowed_inputs",
            value=contract.get("allowed_inputs"),
            expected=ALLOWED_INPUTS,
        )
    )

    errors.extend(
        _validate_exact_string_list(
            field="allowed_outputs",
            value=contract.get("allowed_outputs"),
            expected=ALLOWED_OUTPUTS,
        )
    )

    errors.extend(
        _validate_exact_string_list(
            field="required_drift_dimensions",
            value=contract.get("required_drift_dimensions"),
            expected=REQUIRED_DRIFT_DIMENSIONS,
        )
    )

    errors.extend(
        _validate_exact_string_list(
            field="drift_statuses",
            value=contract.get("drift_statuses"),
            expected=DRIFT_STATUSES,
        )
    )

    errors.extend(
        _validate_exact_string_list(
            field="forbidden_drift_statuses",
            value=contract.get("forbidden_drift_statuses"),
            expected=FORBIDDEN_DRIFT_STATUSES,
        )
    )

    if contract.get("next_stage") != (
        "D2_DRIFT_EVIDENCE_SCHEMA"
    ):
        errors.append("next_stage_mismatch")

    drift_statuses = contract.get("drift_statuses", [])
    forbidden_statuses = contract.get(
        "forbidden_drift_statuses",
        [],
    )

    if (
        isinstance(drift_statuses, list)
        and isinstance(forbidden_statuses, list)
        and set(drift_statuses) & set(forbidden_statuses)
    ):
        errors.append("drift_status_boundary_overlap")

    for field in _REQUIRED_TRUE_FLAGS:
        if contract.get(field) is not True:
            errors.append(f"{field}_must_be_true")

    for field in _REQUIRED_FALSE_FLAGS:
        if contract.get(field) is not False:
            errors.append(f"{field}_must_be_false")

    return sorted(set(errors))