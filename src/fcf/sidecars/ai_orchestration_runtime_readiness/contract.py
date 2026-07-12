"""Readiness-only boundary contract for AI orchestration runtime."""

from typing import Any, Mapping


APP_ID = "AI-ORCHESTRATION-RUNTIME-READINESS-APP-1"
STAGE_ID = "AI-ORCHESTRATION-RUNTIME-READINESS-D1"
CONTRACT_VERSION = "1.0.0"
READINESS_MODE = "READINESS_ONLY"

RUNTIME_READINESS_STATES = (
    "READY_FOR_POLICY_EVALUATION",
    "BLOCKED",
    "DEGRADED",
)

REQUIRED_POLICY_IDENTIFIERS = (
    "FCF.POLICY.RUNTIME.ARCHIVE_AUTHORIZATION_REQUIRED",
    "FCF.POLICY.RUNTIME.CONFIG_SNAPSHOT_REQUIRED",
    "FCF.POLICY.RUNTIME.NO_AUTOMATIC_ROUTING",
    "FCF.POLICY.RUNTIME.NO_EXECUTION_PATH",
    "FCF.POLICY.RUNTIME.NO_MODEL_INVOCATION",
    "FCF.POLICY.RUNTIME.NO_PROMPT_EXECUTION",
    "FCF.POLICY.RUNTIME.OPERATOR_REVIEW_REQUIRED",
    "FCF.POLICY.RUNTIME.READINESS_ONLY",
)

ALLOWED_INPUTS = (
    "REGISTERED_AI_ORCHESTRATION_ROADMAP_ARTIFACT",
    "REGISTERED_CONFIG_SNAPSHOT_REFERENCE",
    "REGISTERED_MODEL_VERSION_ARTIFACT",
    "REGISTERED_POLICY_REFERENCE",
    "REGISTERED_PROMPT_VERSION_ARTIFACT",
    "REGISTERED_VALIDATION_BASELINE_ARTIFACT",
)

ALLOWED_OUTPUTS = (
    "RUNTIME_READINESS_BOUNDARY_CONTRACT",
    "MACHINE_READABLE_ROLE_CONTRACT_MANIFEST",
    "ROUTING_ELIGIBILITY_CONTRACT",
    "TIMEOUT_CONTRACT",
    "RETRY_CONTRACT",
    "FALLBACK_CONTRACT",
    "COST_CONTRACT",
    "POLICY_CONFIG_SNAPSHOT_LINK",
    "RUNTIME_READINESS_REVIEW_PACKET",
    "OPERATOR_HANDOFF",
)

FORBIDDEN_CAPABILITIES = (
    "ACTUAL_MODEL_INVOCATION",
    "ARCHIVE_WRITING",
    "AUTOMATIC_ARCHIVE",
    "AUTOMATIC_CHAMPION_PROMOTION",
    "AUTOMATIC_LEARNING_ACTIVATION",
    "AUTOMATIC_POLICY_ACTIVATION",
    "AUTOMATIC_ROUTING",
    "CORE_MUTATION",
    "P48_EXPANSION",
    "PROMPT_EXECUTION",
    "REAL_EXECUTION",
    "SHADOW_TRADING",
    "TRADE_ACTION",
    "TRADING_API",
    "TRADING_CREDENTIAL_ACCESS",
)

POLICY_CONFIG_LINKAGE = {
    "policy_identifier_required": True,
    "policy_version_required": True,
    "policy_digest_required": True,
    "config_snapshot_id_required": True,
    "startup_policy_check_planned": True,
    "pre_workflow_policy_check_planned": True,
    "fail_closed_behavior_required": True,
    "runtime_policy_enforcement_active": False,
    "automatic_policy_activation_allowed": False,
}

OVERLAP_POLICY = {
    "frozen_core_remains_authoritative": True,
    "existing_sidecars_remain_authoritative": True,
    "ai_orchestration_roadmap_remains_preserved": True,
    "readiness_outputs_are_non_executable": True,
    "runtime_orchestrator_created": False,
    "runtime_workflow_execution_added": False,
    "existing_sidecars_mutated": False,
    "core_mutation_allowed": False,
    "p48_expansion_allowed": False,
}

REQUIRED_TRUE_FLAGS = (
    "blocked_state_required",
    "config_snapshot_linkage_required",
    "degraded_state_required",
    "deterministic_authority_preserved",
    "fail_closed_planning_required",
    "manual_archive_authorization_required",
    "operator_review_required",
    "paper_only",
    "policy_linkage_required",
    "readiness_only",
    "registered_artifacts_only",
    "sidecar_only",
    "source_artifacts_preserved",
)

REQUIRED_FALSE_FLAGS = (
    "actual_model_invocation_allowed",
    "archive_writing_allowed",
    "automatic_archive_allowed",
    "automatic_champion_promotion_allowed",
    "automatic_learning_activation_allowed",
    "automatic_policy_activation_allowed",
    "automatic_routing_allowed",
    "core_mutation_allowed",
    "p48_expansion_allowed",
    "prompt_execution_allowed",
    "real_execution_allowed",
    "runtime_workflow_execution_allowed",
    "shadow_trading_allowed",
    "trade_action_allowed",
    "trading_api_allowed",
    "trading_credentials_allowed",
)

REQUIRED_CONTRACT_FIELDS = (
    "app_id",
    "stage_id",
    "contract_version",
    "readiness_mode",
    "runtime_readiness_states",
    "required_policy_identifiers",
    "allowed_inputs",
    "allowed_outputs",
    "forbidden_capabilities",
    "policy_config_linkage",
    "overlap_policy",
    "safety_flags",
)


def _safety_flags() -> dict[str, bool]:
    return {
        **{name: True for name in REQUIRED_TRUE_FLAGS},
        **{name: False for name in REQUIRED_FALSE_FLAGS},
    }


def build_runtime_readiness_boundary_contract() -> dict[str, Any]:
    """Build the deterministic non-executable D1 contract."""
    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "readiness_mode": READINESS_MODE,
        "runtime_readiness_states": list(RUNTIME_READINESS_STATES),
        "required_policy_identifiers": list(
            REQUIRED_POLICY_IDENTIFIERS
        ),
        "allowed_inputs": list(ALLOWED_INPUTS),
        "allowed_outputs": list(ALLOWED_OUTPUTS),
        "forbidden_capabilities": list(FORBIDDEN_CAPABILITIES),
        "policy_config_linkage": dict(POLICY_CONFIG_LINKAGE),
        "overlap_policy": dict(OVERLAP_POLICY),
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

    expected_names = set(REQUIRED_TRUE_FLAGS + REQUIRED_FALSE_FLAGS)
    if set(value.keys()) != expected_names:
        errors.append("safety_flag_names_must_match_contract")

    return errors


def validate_runtime_readiness_boundary_contract(
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
        "readiness_mode": READINESS_MODE,
    }

    for field, expected in expected_scalars.items():
        if contract.get(field) != expected:
            errors.append(f"{field}_invalid")

    expected_lists = {
        "runtime_readiness_states": list(RUNTIME_READINESS_STATES),
        "required_policy_identifiers": list(
            REQUIRED_POLICY_IDENTIFIERS
        ),
        "allowed_inputs": list(ALLOWED_INPUTS),
        "allowed_outputs": list(ALLOWED_OUTPUTS),
        "forbidden_capabilities": list(FORBIDDEN_CAPABILITIES),
    }

    for field, expected in expected_lists.items():
        if contract.get(field) != expected:
            errors.append(f"{field}_invalid")

    linkage = contract.get("policy_config_linkage")
    if not isinstance(linkage, Mapping):
        errors.append("policy_config_linkage_must_be_mapping")
    elif dict(linkage) != POLICY_CONFIG_LINKAGE:
        errors.append("policy_config_linkage_invalid")

    overlap = contract.get("overlap_policy")
    if not isinstance(overlap, Mapping):
        errors.append("overlap_policy_must_be_mapping")
    elif dict(overlap) != OVERLAP_POLICY:
        errors.append("overlap_policy_invalid")

    errors.extend(
        _validate_safety_flags(contract.get("safety_flags"))
    )

    return errors