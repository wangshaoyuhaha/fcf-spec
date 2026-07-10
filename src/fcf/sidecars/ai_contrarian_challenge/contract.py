"""Boundary contract for deterministic AI contrarian challenge review."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


APP_ID = "AI-CONTRARIAN-CHALLENGE-APP-1"
STAGE_ID = "D1_BOUNDARY_CONTRACT"
CONTRACT_VERSION = "1.0.0"

ALLOWED_INPUTS = (
    "registered_ai_context_artifact",
    "registered_evaluation_result_artifact",
    "registered_comparison_artifact",
    "registered_drift_review_artifact",
    "registered_risk_flags",
    "registered_evidence_references",
)

ALLOWED_OUTPUTS = (
    "challenge_evidence_record",
    "challenge_finding_report",
    "contradiction_summary",
    "challenge_review_packet",
    "challenge_operator_handoff",
)

CHALLENGE_CATEGORIES = (
    "UNSUPPORTED_CLAIM",
    "MISSING_EVIDENCE",
    "LOGICAL_GAP",
    "HIDDEN_RISK",
    "OVERCONFIDENCE",
    "CROSS_ARTIFACT_CONTRADICTION",
)

CHALLENGE_STATUSES = (
    "NO_CHALLENGE",
    "CHALLENGE_FOUND",
    "INSUFFICIENT_EVIDENCE",
    "REVIEW_REQUIRED",
    "INVALID",
    "BLOCKED",
    "ARCHIVED",
)

FORBIDDEN_OUTCOMES = (
    "AUTO_TRUE",
    "AUTO_FALSE",
    "AUTO_WINNER",
    "AUTO_REPLACED_CONCLUSION",
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
    "deterministic_only",
    "registered_artifacts_only",
    "operator_review_required",
    "original_conclusion_preserved",
)

_REQUIRED_FALSE_FLAGS = (
    "core_mutation_allowed",
    "source_artifact_mutation_allowed",
    "model_invocation_allowed",
    "prompt_execution_allowed",
    "orchestrator_execution_allowed",
    "automatic_truth_decision_allowed",
    "automatic_winner_selection_allowed",
    "automatic_conclusion_replacement_allowed",
    "automatic_model_switch_allowed",
    "automatic_prompt_switch_allowed",
    "operator_review_bypass_allowed",
    "trade_action_allowed",
    "real_execution_allowed",
)


def build_boundary_contract() -> dict[str, Any]:
    """Build the immutable D1 contrarian challenge contract."""

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "allowed_inputs": list(ALLOWED_INPUTS),
        "allowed_outputs": list(ALLOWED_OUTPUTS),
        "challenge_categories": list(CHALLENGE_CATEGORIES),
        "challenge_statuses": list(CHALLENGE_STATUSES),
        "forbidden_outcomes": list(FORBIDDEN_OUTCOMES),
        "next_stage": "D2_CHALLENGE_EVIDENCE_SCHEMA",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "deterministic_only": True,
        "registered_artifacts_only": True,
        "operator_review_required": True,
        "original_conclusion_preserved": True,
        "core_mutation_allowed": False,
        "source_artifact_mutation_allowed": False,
        "model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "orchestrator_execution_allowed": False,
        "automatic_truth_decision_allowed": False,
        "automatic_winner_selection_allowed": False,
        "automatic_conclusion_replacement_allowed": False,
        "automatic_model_switch_allowed": False,
        "automatic_prompt_switch_allowed": False,
        "operator_review_bypass_allowed": False,
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

    if any(
        not isinstance(item, str) or not item.strip()
        for item in value
    ):
        return [f"{field}_invalid"]

    errors: list[str] = []

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
    """Return deterministic boundary validation errors."""

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
            field="challenge_categories",
            value=contract.get("challenge_categories"),
            expected=CHALLENGE_CATEGORIES,
        )
    )

    errors.extend(
        _validate_exact_string_list(
            field="challenge_statuses",
            value=contract.get("challenge_statuses"),
            expected=CHALLENGE_STATUSES,
        )
    )

    errors.extend(
        _validate_exact_string_list(
            field="forbidden_outcomes",
            value=contract.get("forbidden_outcomes"),
            expected=FORBIDDEN_OUTCOMES,
        )
    )

    if contract.get("next_stage") != (
        "D2_CHALLENGE_EVIDENCE_SCHEMA"
    ):
        errors.append("next_stage_mismatch")

    challenge_statuses = contract.get(
        "challenge_statuses",
        [],
    )
    forbidden_outcomes = contract.get(
        "forbidden_outcomes",
        [],
    )

    if (
        isinstance(challenge_statuses, list)
        and isinstance(forbidden_outcomes, list)
        and set(challenge_statuses) & set(forbidden_outcomes)
    ):
        errors.append("status_outcome_boundary_overlap")

    for field in _REQUIRED_TRUE_FLAGS:
        if contract.get(field) is not True:
            errors.append(f"{field}_must_be_true")

    for field in _REQUIRED_FALSE_FLAGS:
        if contract.get(field) is not False:
            errors.append(f"{field}_must_be_false")

    return sorted(set(errors))