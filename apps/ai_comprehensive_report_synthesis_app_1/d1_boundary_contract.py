from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

APP_ID = "AI-COMPREHENSIVE-REPORT-SYNTHESIS-APP-1"
STAGE_ID = "D1"
CONTRACT_VERSION = "1.0.0"


REQUIRED_BOUNDARIES = {
    "paper_only": True,
    "local_only": True,
    "read_only": True,
    "sidecar_only": True,
    "deterministic_only": True,
    "registered_artifacts_only": True,
    "operator_review_required": True,
    "source_artifacts_preserved": True,
    "original_conclusions_preserved": True,
}


FORBIDDEN_PERMISSIONS = {
    "core_mutation": False,
    "source_artifact_mutation": False,
    "claim_invention": False,
    "evidence_invention": False,
    "causality_inference_from_correlation": False,
    "automatic_causal_truth_decision": False,
    "probability_assignment": False,
    "winner_selection": False,
    "conclusion_replacement": False,
    "risk_flag_deletion": False,
    "risk_flag_downgrade": False,
    "live_model_invocation": False,
    "prompt_execution": False,
    "runtime_orchestrator_execution": False,
    "automatic_routing": False,
    "automatic_role_switching": False,
    "automatic_archive_execution": False,
    "trade_action": False,
    "real_execution": False,
    "tag": False,
    "release": False,
    "deploy": False,
}


REQUIRED_GOVERNANCE_STATES = {
    "causal_truth": "UNDETERMINED",
    "probability": "NOT_ASSIGNED",
    "winner": "NOT_SELECTED",
    "operator_review": "REQUIRED",
    "operator_decision": "PENDING",
    "archive_execution": "NOT_PERFORMED",
}


ANTI_OVERLAP_RULES = {
    "report_archive_authority": "NOT_GRANTED",
    "operator_decision_authority": "NOT_GRANTED",
    "upstream_artifact_mutation": "FORBIDDEN",
    "runtime_orchestration_authority": "NOT_GRANTED",
    "source_conclusion_rewrite": "FORBIDDEN",
}


class ContractViolation(ValueError):
    """Raised when the D1 synthesis boundary contract is invalid."""


def build_d1_contract() -> dict[str, Any]:
    """Build the deterministic D1 boundary contract."""

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "status": "D1_COMPLETE",
        "purpose": (
            "Assemble registered source artifacts into a deterministic, "
            "paper-only comprehensive governance report."
        ),
        "boundaries": deepcopy(REQUIRED_BOUNDARIES),
        "permissions": deepcopy(FORBIDDEN_PERMISSIONS),
        "governance_states": deepcopy(REQUIRED_GOVERNANCE_STATES),
        "anti_overlap_rules": deepcopy(ANTI_OVERLAP_RULES),
    }


def _validate_exact_mapping(
    name: str,
    actual: object,
    expected: Mapping[str, object],
) -> list[str]:
    if not isinstance(actual, Mapping):
        return [f"{name} must be a mapping"]

    errors: list[str] = []

    for key, expected_value in expected.items():
        if key not in actual:
            errors.append(f"{name}.{key} is missing")
            continue

        if actual[key] != expected_value:
            errors.append(
                f"{name}.{key} must be {expected_value!r}, "
                f"found {actual[key]!r}"
            )

    unexpected = sorted(set(actual) - set(expected))
    for key in unexpected:
        errors.append(f"{name}.{key} is not registered")

    return errors


def validate_d1_contract(contract: Mapping[str, object]) -> tuple[str, ...]:
    """Return deterministic validation errors for the D1 contract."""

    errors: list[str] = []

    expected_scalars = {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "status": "D1_COMPLETE",
    }

    for key, expected_value in expected_scalars.items():
        actual_value = contract.get(key)

        if actual_value != expected_value:
            errors.append(
                f"{key} must be {expected_value!r}, "
                f"found {actual_value!r}"
            )

    purpose = contract.get("purpose")
    if not isinstance(purpose, str) or not purpose.strip():
        errors.append("purpose must be a non-empty string")

    errors.extend(
        _validate_exact_mapping(
            "boundaries",
            contract.get("boundaries"),
            REQUIRED_BOUNDARIES,
        )
    )
    errors.extend(
        _validate_exact_mapping(
            "permissions",
            contract.get("permissions"),
            FORBIDDEN_PERMISSIONS,
        )
    )
    errors.extend(
        _validate_exact_mapping(
            "governance_states",
            contract.get("governance_states"),
            REQUIRED_GOVERNANCE_STATES,
        )
    )
    errors.extend(
        _validate_exact_mapping(
            "anti_overlap_rules",
            contract.get("anti_overlap_rules"),
            ANTI_OVERLAP_RULES,
        )
    )

    return tuple(errors)


def require_valid_d1_contract(
    contract: Mapping[str, object],
) -> Mapping[str, object]:
    """Require a valid D1 contract without mutating the source mapping."""

    errors = validate_d1_contract(contract)

    if errors:
        raise ContractViolation("; ".join(errors))

    return contract