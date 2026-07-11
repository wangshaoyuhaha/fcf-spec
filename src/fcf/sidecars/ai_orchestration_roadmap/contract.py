"""Planning-only boundary contract for AI orchestration roadmap."""

from typing import Any, Mapping


APP_ID = "AI-ORCHESTRATION-ROADMAP-APP-1"
STAGE_ID = "AI-ORCHESTRATION-ROADMAP-D1"
CONTRACT_VERSION = "1.0.0"
ROADMAP_MODE = "PLANNING_ONLY"

ALLOWED_INPUTS = (
    "REGISTERED_AI_CONTEXT_ARTIFACT",
    "REGISTERED_AI_EVALUATION_ARTIFACT",
    "REGISTERED_AI_CHALLENGE_ARTIFACT",
    "REGISTERED_MARKET_NARRATIVE_ARTIFACT",
    "REGISTERED_SCENARIO_SIMULATION_ARTIFACT",
    "REGISTERED_MODEL_VERSION_ARTIFACT",
    "REGISTERED_PROMPT_VERSION_ARTIFACT",
    "REGISTERED_VALIDATION_BASELINE_ARTIFACT",
    "REGISTERED_CORRELATION_ROLLUP_ARTIFACT",
    "REGISTERED_OPERATOR_REVIEW_ARTIFACT",
)

ALLOWED_OUTPUTS = (
    "ROADMAP_BOUNDARY_CONTRACT",
    "REGISTERED_ARTIFACT_DEPENDENCY_PLAN",
    "DETERMINISTIC_GOVERNANCE_DAG_PLAN",
    "OPERATOR_GATE_PLAN",
    "FAILURE_AND_DEGRADATION_PLAN",
    "MODEL_ROLE_RESPONSIBILITY_MATRIX",
    "ROADMAP_REVIEW_PACKET",
    "OPERATOR_HANDOFF",
)

FORBIDDEN_CAPABILITIES = (
    "AI_ORCHESTRATOR_EXECUTION",
    "AUTOMATIC_MODEL_SELECTION",
    "AUTOMATIC_MODEL_SWITCHING",
    "AUTOMATIC_PROMPT_SELECTION",
    "AUTOMATIC_PROMPT_SWITCHING",
    "AUTOMATIC_ROLE_SWITCHING",
    "AUTOMATIC_ROUTE_SELECTION",
    "AUTOMATIC_TRUTH_DECISION",
    "AUTOMATIC_WINNER_SELECTION",
    "AUTOMATIC_PROBABILITY_ASSIGNMENT",
    "AUTOMATIC_SCENARIO_RANKING",
    "CONCLUSION_REPLACEMENT",
    "CORE_MUTATION",
    "LIVE_MODEL_INVOCATION",
    "OPERATOR_REVIEW_BYPASS",
    "PROMPT_EXECUTION",
    "REAL_EXECUTION",
    "RUNTIME_WORKFLOW_EXECUTION",
    "TRADE_ACTION",
)

REQUIRED_TRUE_FLAGS = (
    "deterministic_only",
    "local_only",
    "operator_review_required",
    "original_conclusions_preserved",
    "paper_only",
    "planning_only",
    "read_only",
    "registered_artifacts_only",
    "roadmap_outputs_non_executable",
    "sidecar_only",
    "source_artifacts_preserved",
)

REQUIRED_FALSE_FLAGS = (
    "ai_orchestrator_execution_allowed",
    "automatic_model_selection_allowed",
    "automatic_model_switching_allowed",
    "automatic_probability_assignment_allowed",
    "automatic_prompt_selection_allowed",
    "automatic_prompt_switching_allowed",
    "automatic_ranking_allowed",
    "automatic_role_switching_allowed",
    "automatic_route_selection_allowed",
    "automatic_truth_decision_allowed",
    "automatic_winner_selection_allowed",
    "conclusion_replacement_allowed",
    "core_mutation_allowed",
    "live_model_invocation_allowed",
    "operator_review_bypass_allowed",
    "prompt_execution_allowed",
    "real_execution_allowed",
    "runtime_workflow_execution_allowed",
    "trade_action_allowed",
)

OVERLAP_POLICY = {
    "research_workflow_app_remains_authoritative": True,
    "existing_sidecars_remain_authoritative": True,
    "roadmap_outputs_are_non_executable": True,
    "runtime_orchestrator_created": False,
    "runtime_workflow_execution_added": False,
    "existing_sidecars_mutated": False,
    "core_mutation_allowed": False,
}

REQUIRED_CONTRACT_FIELDS = (
    "app_id",
    "stage_id",
    "contract_version",
    "roadmap_mode",
    "allowed_inputs",
    "allowed_outputs",
    "forbidden_capabilities",
    "overlap_policy",
    "safety_flags",
)


def _safety_flags() -> dict[str, bool]:
    return {
        **{name: True for name in REQUIRED_TRUE_FLAGS},
        **{name: False for name in REQUIRED_FALSE_FLAGS},
    }


def build_roadmap_boundary_contract() -> dict[str, Any]:
    """Build a deterministic planning-only boundary contract."""
    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "roadmap_mode": ROADMAP_MODE,
        "allowed_inputs": list(ALLOWED_INPUTS),
        "allowed_outputs": list(ALLOWED_OUTPUTS),
        "forbidden_capabilities": list(
            FORBIDDEN_CAPABILITIES
        ),
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

    expected_names = set(
        REQUIRED_TRUE_FLAGS + REQUIRED_FALSE_FLAGS
    )

    if set(value.keys()) != expected_names:
        errors.append("safety_flag_names_must_match_contract")

    return errors


def validate_roadmap_boundary_contract(
    contract: object,
) -> list[str]:
    """Return deterministic D1 boundary validation errors."""
    if not isinstance(contract, Mapping):
        return ["contract_must_be_mapping"]

    errors: list[str] = []

    if set(contract.keys()) != set(REQUIRED_CONTRACT_FIELDS):
        errors.append("contract_fields_must_match_schema")

    expected_scalars = {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "roadmap_mode": ROADMAP_MODE,
    }

    for field, expected in expected_scalars.items():
        if contract.get(field) != expected:
            errors.append(f"{field}_invalid")

    expected_lists = {
        "allowed_inputs": list(ALLOWED_INPUTS),
        "allowed_outputs": list(ALLOWED_OUTPUTS),
        "forbidden_capabilities": list(
            FORBIDDEN_CAPABILITIES
        ),
    }

    for field, expected in expected_lists.items():
        if contract.get(field) != expected:
            errors.append(f"{field}_invalid")

    overlap_policy = contract.get("overlap_policy")

    if not isinstance(overlap_policy, Mapping):
        errors.append("overlap_policy_must_be_mapping")
    elif dict(overlap_policy) != OVERLAP_POLICY:
        errors.append("overlap_policy_invalid")

    errors.extend(
        _validate_safety_flags(
            contract.get("safety_flags")
        )
    )

    return errors
