"""Planning-only boundary contract for multi-model workflow design."""

import re
from typing import Any, Mapping

APP_ID = "AI-MULTI-MODEL-WORKFLOW-PLANNING-APP-1"
STAGE_ID = "AI-MULTI-MODEL-WORKFLOW-PLANNING-D1"
CONTRACT_VERSION = "1.0.0"
PLANNING_MODE = "PLANNING_ONLY"
WORKFLOW_STATUS = "DESIGN_ONLY"

MODEL_SLOT_TYPES = (
    "PRIMARY",
    "FALLBACK",
    "COMPARISON",
    "LOCAL_ONLY",
    "CLOUD_APPROVED",
)

MODEL_SLOT_SEMANTICS = {
    "PRIMARY": "PLANNED_PRIMARY_ASSIGNMENT",
    "FALLBACK": "PLANNED_FALLBACK_ASSIGNMENT",
    "COMPARISON": "PLANNED_COMPARISON_ASSIGNMENT",
    "LOCAL_ONLY": "DETERMINISTIC_LOCAL_RESTRICTION",
    "CLOUD_APPROVED": "DETERMINISTIC_POLICY_ELIGIBILITY_ONLY",
}

AUTHORITY_HIERARCHY = (
    "OPERATOR_POLICY",
    "FCF_HARD_POLICY",
    "DETERMINISTIC_ENGINE",
    "VALIDATED_DATA_AND_EVIDENCE",
    "ORCHESTRATOR",
    "AI_MODELS",
    "EXTERNAL_NARRATIVE",
)

REQUIRED_EXISTING_BINDINGS = (
    "MACHINE_READABLE_ROLE_CONTRACT_MANIFEST",
    "REGISTERED_MODEL_VERSION_ARTIFACT",
    "REGISTERED_PROMPT_VERSION_ARTIFACT",
    "REGISTERED_POLICY_REFERENCE",
    "REGISTERED_CONFIG_SNAPSHOT_REFERENCE",
    "ROUTING_ELIGIBILITY_CONTRACT",
)

INPUT_OWNERSHIP = {
    "MACHINE_READABLE_ROLE_CONTRACT_MANIFEST": (
        "AI-ORCHESTRATION-RUNTIME-READINESS-APP-1"
    ),
    "REGISTERED_MODEL_VERSION_ARTIFACT": (
        "AI-PROMPT-MODEL-VERSION-REGISTRY-APP-1"
    ),
    "REGISTERED_PROMPT_VERSION_ARTIFACT": (
        "AI-PROMPT-MODEL-VERSION-REGISTRY-APP-1"
    ),
    "REGISTERED_POLICY_REFERENCE": "FCF_HARD_POLICY",
    "REGISTERED_CONFIG_SNAPSHOT_REFERENCE": (
        "REGISTERED_CONFIG_SNAPSHOT"
    ),
    "ROUTING_ELIGIBILITY_CONTRACT": (
        "AI-ORCHESTRATION-RUNTIME-READINESS-APP-1"
    ),
}

OUTPUT_OWNERSHIP = {
    "MULTI_MODEL_WORKFLOW_BOUNDARY_CONTRACT": APP_ID,
    "FINAL_OPERATOR_APPROVAL_RECORD": "HUMAN_OPERATOR",
}

CLOUD_ELIGIBILITY_RULES = {
    "deterministic_policy_decision_required": True,
    "privacy_policy_status_required": True,
    "licensing_policy_status_required": True,
    "registered_artifacts_required": True,
    "config_snapshot_required": True,
    "operator_review_required": True,
    "fail_closed_required": True,
    "ai_self_authorization_allowed": False,
    "automatic_cloud_selection_allowed": False,
    "automatic_cloud_switching_allowed": False,
}

NON_DUPLICATION_RULES = {
    "existing_role_contracts_reused": True,
    "existing_version_registry_reused": True,
    "existing_routing_eligibility_reused": True,
    "new_role_registry_created": False,
    "new_model_registry_created": False,
    "new_prompt_registry_created": False,
    "runtime_readiness_reimplemented": False,
}

FORBIDDEN_CAPABILITIES = (
    "ACTUAL_MODEL_INVOCATION",
    "ARCHIVE_WRITING",
    "AUTOMATIC_ARCHIVE",
    "AUTOMATIC_MODEL_SELECTION",
    "AUTOMATIC_MODEL_SWITCHING",
    "AUTOMATIC_ROUTING",
    "BALANCE_ACCESS",
    "CORE_MUTATION",
    "CREDENTIAL_ACCESS",
    "HTTP_SERVICE",
    "P48_EXPANSION",
    "PORT_LISTENER",
    "POSITION_ACCESS",
    "PROMPT_EXECUTION",
    "REAL_EXECUTION",
    "REAL_ORDER",
    "RUNTIME_ACTIVATION",
    "TRADING_API",
    "WALLET_ACCESS",
)

REQUIRED_TRUE_FLAGS = (
    "config_snapshot_binding_required",
    "deterministic_authority_preserved",
    "existing_role_contracts_bound",
    "fail_closed_cloud_eligibility_required",
    "input_ownership_required",
    "model_version_binding_required",
    "operator_review_required",
    "output_ownership_required",
    "paper_only",
    "planning_only",
    "policy_binding_required",
    "prompt_version_binding_required",
    "read_only",
    "registered_artifacts_only",
    "sidecar_only",
)

REQUIRED_FALSE_FLAGS = (
    "archive_writing_allowed",
    "automatic_archive_allowed",
    "automatic_model_selection_allowed",
    "automatic_model_switching_allowed",
    "automatic_routing_allowed",
    "balance_access_allowed",
    "core_mutation_allowed",
    "credential_access_allowed",
    "http_service_allowed",
    "model_invocation_allowed",
    "p48_expansion_allowed",
    "port_listener_allowed",
    "position_access_allowed",
    "prompt_execution_allowed",
    "real_execution_allowed",
    "real_order_allowed",
    "runtime_activation_allowed",
    "trading_api_allowed",
    "wallet_access_allowed",
)

REQUIRED_CONTRACT_FIELDS = (
    "contract_id",
    "app_id",
    "stage_id",
    "contract_version",
    "planning_mode",
    "workflow_status",
    "model_slot_types",
    "model_slot_semantics",
    "authority_hierarchy",
    "required_existing_bindings",
    "input_ownership",
    "output_ownership",
    "cloud_eligibility_rules",
    "non_duplication_rules",
    "forbidden_capabilities",
    "operator_review_status",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class MultiModelWorkflowBoundaryViolation(ValueError):
    """Raised when the planning-only workflow contract is invalid."""


def _safety_flags() -> dict[str, bool]:
    return {
        **{name: True for name in REQUIRED_TRUE_FLAGS},
        **{name: False for name in REQUIRED_FALSE_FLAGS},
    }


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def build_multi_model_workflow_boundary_contract(
    *,
    contract_id: str = "fcf.multi_model_workflow.planning.v1",
) -> dict[str, Any]:
    """Build the deterministic non-executable D1 contract."""
    if not _valid_identifier(contract_id):
        raise MultiModelWorkflowBoundaryViolation(
            "contract_id_invalid"
        )

    return {
        "contract_id": contract_id,
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "planning_mode": PLANNING_MODE,
        "workflow_status": WORKFLOW_STATUS,
        "model_slot_types": list(MODEL_SLOT_TYPES),
        "model_slot_semantics": dict(MODEL_SLOT_SEMANTICS),
        "authority_hierarchy": list(AUTHORITY_HIERARCHY),
        "required_existing_bindings": list(
            REQUIRED_EXISTING_BINDINGS
        ),
        "input_ownership": dict(INPUT_OWNERSHIP),
        "output_ownership": dict(OUTPUT_OWNERSHIP),
        "cloud_eligibility_rules": dict(
            CLOUD_ELIGIBILITY_RULES
        ),
        "non_duplication_rules": dict(NON_DUPLICATION_RULES),
        "forbidden_capabilities": list(FORBIDDEN_CAPABILITIES),
        "operator_review_status": "REVIEW_REQUIRED",
        "safety_flags": _safety_flags(),
    }


def _validate_safety_flags(value: Any) -> list[str]:
    if not isinstance(value, Mapping):
        return ["safety_flags_must_be_mapping"]

    errors: list[str] = []

    for name in REQUIRED_TRUE_FLAGS:
        if value.get(name) is not True:
            errors.append(f"{name}_must_be_true")

    for name in REQUIRED_FALSE_FLAGS:
        if value.get(name) is not False:
            errors.append(f"{name}_must_be_false")

    expected_names = set(
        REQUIRED_TRUE_FLAGS + REQUIRED_FALSE_FLAGS
    )
    if set(value.keys()) != expected_names:
        errors.append("safety_flag_names_must_match_contract")

    return errors


def validate_multi_model_workflow_boundary_contract(
    contract: object,
) -> list[str]:
    """Return deterministic D1 validation errors."""
    if not isinstance(contract, Mapping):
        return ["contract_must_be_mapping"]

    errors: list[str] = []

    if set(contract.keys()) != set(REQUIRED_CONTRACT_FIELDS):
        errors.append("contract_fields_must_match_schema")

    expected_scalars = {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "planning_mode": PLANNING_MODE,
        "workflow_status": WORKFLOW_STATUS,
        "operator_review_status": "REVIEW_REQUIRED",
    }

    for field, expected in expected_scalars.items():
        if contract.get(field) != expected:
            errors.append(f"{field}_invalid")

    if not _valid_identifier(contract.get("contract_id")):
        errors.append("contract_id_invalid")

    expected_lists = {
        "model_slot_types": list(MODEL_SLOT_TYPES),
        "authority_hierarchy": list(AUTHORITY_HIERARCHY),
        "required_existing_bindings": list(
            REQUIRED_EXISTING_BINDINGS
        ),
        "forbidden_capabilities": list(FORBIDDEN_CAPABILITIES),
    }

    for field, expected in expected_lists.items():
        if contract.get(field) != expected:
            errors.append(f"{field}_invalid")

    expected_mappings = {
        "model_slot_semantics": MODEL_SLOT_SEMANTICS,
        "input_ownership": INPUT_OWNERSHIP,
        "output_ownership": OUTPUT_OWNERSHIP,
        "cloud_eligibility_rules": CLOUD_ELIGIBILITY_RULES,
        "non_duplication_rules": NON_DUPLICATION_RULES,
    }

    for field, expected in expected_mappings.items():
        value = contract.get(field)
        if not isinstance(value, Mapping):
            errors.append(f"{field}_must_be_mapping")
        elif dict(value) != expected:
            errors.append(f"{field}_invalid")

    errors.extend(
        _validate_safety_flags(contract.get("safety_flags"))
    )

    return errors